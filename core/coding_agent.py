from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any

import requests

from core.coding_progress import (
    set_coding_progress,
)


# =========================================================
# CONFIGURATION
# =========================================================

OLLAMA_BASE_URL = os.environ.get(
    "JARVIS_OLLAMA_URL",
    "http://localhost:11434",
).rstrip("/")

OLLAMA_CHAT_URL = f"{OLLAMA_BASE_URL}/api/chat"
OLLAMA_TAGS_URL = f"{OLLAMA_BASE_URL}/api/tags"

PROJECTS_ROOT = (
    Path.home()
    / "Documents"
    / "JARVIS Projects"
)

MAX_PROJECT_FILES = 60
MAX_FILE_CHARS = 600_000
MAX_CONTEXT_CHARS = 36_000
MAX_REPAIR_ROUNDS = 3
DEFAULT_TIMEOUT = 240

PREFERRED_CODING_MODELS = (
    "qwen2.5-coder:14b",
    "qwen2.5-coder:7b",
    "qwen2.5-coder:3b",
    "deepseek-coder-v2:16b",
    "codellama:13b",
)


# =========================================================
# RESULT TYPES
# =========================================================

@dataclass
class ValidationIssue:
    path: str
    message: str
    output: str = ""


@dataclass
class CodingAgentResult:
    success: bool
    message: str
    project_dir: str = ""
    files_created: list[str] = field(default_factory=list)
    issues: list[ValidationIssue] = field(default_factory=list)
    model: str = ""


# =========================================================
# PROMPTS
# =========================================================

CODING_SYSTEM_PROMPT = """
You are JARVIS Coding Agent, a senior software engineer.

Your job is to design and implement real software, not just
produce snippets. Think about architecture, dependencies,
error handling, maintainability, security, and how files fit
together.

When generating a project:
- Keep the architecture coherent.
- Use sensible filenames and directories.
- Keep imports consistent with the project structure.
- Prefer standard library solutions when practical.
- Do not invent APIs or packages unnecessarily.
- Include tests when they are useful.
- Include a README for non-trivial projects.
- Never use unsafe absolute paths in generated project plans.
- Never put secrets, API keys, or passwords into source files.
- Return exactly the format requested by the current task.
""".strip()


def build_inline_code_prompt(request: str, window_context: str = "") -> str:
    return f"""
{CODING_SYSTEM_PROMPT}

The user wants code for the following request:
{request}

Current editor/window context:
{window_context or "No editor context was provided."}

Return ONLY the complete code or file content.
Do not use Markdown code fences.
Do not add an explanation before or after the code.
""".strip()


def build_project_prompt(request: str) -> str:
    return f"""
{CODING_SYSTEM_PROMPT}

Design a project for this request:
{request}

Return ONLY valid JSON with this exact structure:

{{
  "project_name": "short_name",
  "language": "primary language",
  "summary": "one paragraph",
  "files": [
    {{
      "path": "relative/path.ext",
      "purpose": "what this file is responsible for"
    }}
  ]
}}

Rules:
- Return a project plan, not file contents yet.
- Use relative paths only.
- Never use .. path traversal.
- Keep the number of files reasonable.
- Include all files genuinely needed to make the project usable.
- Include tests for meaningful application logic.
- Include README.md for non-trivial projects.
""".strip()


def _build_file_prompt(
    user_request: str,
    plan: dict[str, Any],
    target_path: str,
    purpose: str,
    existing_files: dict[str, str],
) -> str:
    context_parts: list[str] = []

    for path, content in existing_files.items():
        context_parts.append(
            f"\n--- {path} ---\n{content[:8000]}\n--- END {path} ---"
        )

    existing_context = "".join(context_parts)
    if len(existing_context) > MAX_CONTEXT_CHARS:
        existing_context = existing_context[:MAX_CONTEXT_CHARS]

    return f"""
{CODING_SYSTEM_PROMPT}

USER REQUEST:
{user_request}

PROJECT PLAN:
{json.dumps(plan, indent=2)}

YOU ARE GENERATING THIS FILE:
{target_path}

FILE PURPOSE:
{purpose}

ALREADY GENERATED FILES:
{existing_context or "None yet."}

Write the COMPLETE contents of {target_path}.

Important:
- Make this file work with the other files already generated.
- Use correct imports for the project structure.
- Do not leave TODO placeholders for required functionality.
- Do not return Markdown fences.
- Do not explain the file.
- Return ONLY the file contents.
""".strip()


def _build_repair_prompt(
    user_request: str,
    plan: dict[str, Any],
    path: str,
    content: str,
    issue: ValidationIssue,
    project_files: dict[str, str],
) -> str:
    related_parts: list[str] = []

    for file_path, file_content in project_files.items():
        if file_path == path:
            continue
        related_parts.append(
            f"\n--- {file_path} ---\n{file_content[:6000]}\n--- END {file_path} ---"
        )

    related = "".join(related_parts)
    if len(related) > MAX_CONTEXT_CHARS:
        related = related[:MAX_CONTEXT_CHARS]

    return f"""
{CODING_SYSTEM_PROMPT}

You are repairing an existing project.

USER REQUEST:
{user_request}

PROJECT PLAN:
{json.dumps(plan, indent=2)}

FILE WITH THE PROBLEM:
{path}

CURRENT FILE:
---
{content}
---

VALIDATION ERROR:
{issue.message}

VALIDATION OUTPUT:
{issue.output}

RELATED FILES:
{related or "None provided."}

Return ONLY the complete corrected contents of {path}.
Do not use Markdown fences.
Do not explain what you changed.
""".strip()


# =========================================================
# HELPERS
# =========================================================


def _extract_json(text: str) -> dict[str, Any]:
    cleaned = str(text or "").strip()

    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\s*```$", "", cleaned)

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start < 0 or end <= start:
        raise ValueError("AI did not return a JSON object.")

    payload = json.loads(cleaned[start : end + 1])

    if not isinstance(payload, dict):
        raise ValueError("AI returned a JSON value instead of an object.")

    return payload


def _extract_code(text: str) -> str:
    cleaned = str(text or "").strip()

    match = re.match(
        r"^```[A-Za-z0-9_+.#-]*\s*\n?(.*?)\n?```$",
        cleaned,
        flags=re.DOTALL,
    )

    if match:
        cleaned = match.group(1).strip("\n")

    return cleaned


def _safe_project_name(name: Any) -> str:
    value = str(name or "jarvis_project").strip()

    value = re.sub(
        r"[^A-Za-z0-9._ -]+",
        "",
        value,
    )
    value = re.sub(r"\s+", "_", value)
    value = value.strip("._-")

    return (value or "jarvis_project")[:60]


def _unique_project_dir(project_name: str) -> Path:
    PROJECTS_ROOT.mkdir(parents=True, exist_ok=True)

    base = PROJECTS_ROOT / project_name

    if not base.exists():
        return base

    index = 2
    while True:
        candidate = PROJECTS_ROOT / f"{project_name}_{index}"
        if not candidate.exists():
            return candidate
        index += 1


def _safe_relative_path(value: Any) -> Path | None:
    normalized = str(value or "").replace("\\", "/").strip()
    pure = PurePosixPath(normalized)

    if pure.is_absolute() or ".." in pure.parts:
        return None

    cleaned = [part for part in pure.parts if part not in ("", ".")]

    if not cleaned:
        return None

    # Avoid accidental Windows drive-like paths.
    if ":" in cleaned[0]:
        return None

    return Path(*cleaned)


def _is_probably_text_file(path: Path) -> bool:
    return path.suffix.lower() in {
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".json",
        ".html",
        ".htm",
        ".css",
        ".scss",
        ".md",
        ".txt",
        ".yaml",
        ".yml",
        ".toml",
        ".ini",
        ".xml",
        ".sql",
        ".sh",
        ".bat",
        ".ps1",
        ".env.example",
        ".gitignore",
    }


def _read_project_files(project_dir: Path) -> dict[str, str]:
    files: dict[str, str] = {}

    for path in project_dir.rglob("*"):
        if not path.is_file():
            continue
        if not _is_probably_text_file(path):
            continue

        try:
            files[str(path.relative_to(project_dir)).replace("\\", "/")] = (
                path.read_text(encoding="utf-8")
            )
        except (OSError, UnicodeError):
            continue

    return files


def _get_installed_ollama_models() -> list[str]:
    try:
        response = requests.get(
            OLLAMA_TAGS_URL,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        models = data.get("models", [])
        if not isinstance(models, list):
            return []

        result: list[str] = []
        for item in models:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name", "")).strip()
            if name:
                result.append(name)

        return result

    except Exception:
        return []


def _fallback_ai_model() -> str:
    try:
        from core.ai_mode import get_current_model

        model = str(get_current_model() or "").strip()
        if model:
            return model
    except Exception:
        pass

    return "qwen2.5:1.5b"


def _choose_coding_model(requested_model: str | None = None) -> str:
    explicit = str(
        requested_model
        or os.environ.get("JARVIS_CODING_MODEL", "")
    ).strip()

    if explicit:
        return explicit

    installed = _get_installed_ollama_models()
    installed_lower = {name.lower(): name for name in installed}

    # Respect the Coding Agent model selected in JARVIS Settings
    # when that model is actually installed.
    try:
        from core.ai_mode import get_coding_model

        configured = str(
            get_coding_model()
            or ""
        ).strip()

        if configured:
            configured_name = installed_lower.get(
                configured.lower()
            )

            if configured_name:
                return configured_name
    except Exception:
        pass

    for preferred in PREFERRED_CODING_MODELS:
        if preferred.lower() in installed_lower:
            return installed_lower[preferred.lower()]

    # Prefer anything installed with a coding-oriented name.
    for model in installed:
        lowered = model.lower()
        if any(
            marker in lowered
            for marker in (
                "coder",
                "code",
                "codestral",
                "devstral",
            )
        ):
            return model

    return _fallback_ai_model()


def _run_process(
    args: list[str],
    cwd: Path,
    timeout: int,
) -> tuple[int, str]:
    creationflags = (
        subprocess.CREATE_NO_WINDOW
        if os.name == "nt"
        else 0
    )

    try:
        result = subprocess.run(
            args,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
            creationflags=creationflags,
        )

        output = (
            (result.stdout or "")
            + ("\n" if result.stdout and result.stderr else "")
            + (result.stderr or "")
        ).strip()

        return result.returncode, output

    except subprocess.TimeoutExpired as error:
        return 124, f"Process timed out after {timeout} seconds. {error}"
    except Exception as error:
        return 1, str(error)


# =========================================================
# CODING AGENT
# =========================================================

class CodingAgent:
    """Dedicated JARVIS software-engineering agent."""

    def __init__(
        self,
        model: str | None = None,
        timeout: int = DEFAULT_TIMEOUT,
        repair_rounds: int = MAX_REPAIR_ROUNDS,
        auto_open: bool = True,
    ) -> None:
        self.model = _choose_coding_model(model)
        self.timeout = max(30, int(timeout))
        self.repair_rounds = max(0, int(repair_rounds))
        self.auto_open = bool(auto_open)

    # =====================================================
    # OLLAMA
    # =====================================================

    def _chat(
        self,
        user_prompt: str,
        temperature: float = 0.15,
    ) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": CODING_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "stream": False,
            "keep_alive": "10m",
            "options": {
                "temperature": temperature,
            },
        }

        response = requests.post(
            OLLAMA_CHAT_URL,
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()
        message = data.get("message", {})

        if not isinstance(message, dict):
            raise RuntimeError("Ollama returned an invalid message object.")

        content = str(message.get("content", "")).strip()

        if not content:
            raise RuntimeError("Ollama returned an empty coding response.")

        return content

    def _chat_stream_to_file(
        self,
        user_prompt: str,
        target: Path,
        temperature: float = 0.12,
    ) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": CODING_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "stream": True,
            "keep_alive": "10m",
            "options": {
                "temperature": temperature,
            },
        }

        response = requests.post(
            OLLAMA_CHAT_URL,
            json=payload,
            timeout=self.timeout,
            stream=True,
        )
        response.raise_for_status()

        chunks = []

        with open(
            target,
            "w",
            encoding="utf-8",
        ) as file:
            for line in response.iter_lines(
                decode_unicode=True
            ):
                if not line:
                    continue

                data = json.loads(line)

                message = data.get(
                    "message",
                    {}
                )

                if not isinstance(message, dict):
                    continue

                chunk = str(
                    message.get(
                        "content",
                        ""
                    )
                )

                if chunk:
                    chunks.append(chunk)
                    file.write(chunk)
                    file.flush()

                if data.get("done"):
                    break

        content = "".join(chunks)

        if len(content) > MAX_FILE_CHARS:
            content = content[:MAX_FILE_CHARS]

        cleaned = _extract_code(content)

        if cleaned != content:
            target.write_text(
                cleaned,
                encoding="utf-8",
            )

        return cleaned

    # =====================================================
    # PROJECT PLANNING
    # =====================================================

    def plan_project(
self, request: str) -> dict[str, Any]:
        response = self._chat(
            build_project_prompt(request),
            temperature=0.10,
        )

        plan = _extract_json(response)

        files = plan.get("files")
        if not isinstance(files, list) or not files:
            raise ValueError("The coding agent did not return any project files.")

        safe_files: list[dict[str, str]] = []

        for item in files[:MAX_PROJECT_FILES]:
            if not isinstance(item, dict):
                continue

            path = _safe_relative_path(item.get("path"))
            if path is None:
                continue

            purpose = str(item.get("purpose", "")).strip()
            safe_files.append(
                {
                    "path": str(path).replace("\\", "/"),
                    "purpose": purpose or "Project file.",
                }
            )

        if not safe_files:
            raise ValueError("The coding agent did not return safe file paths.")

        plan["project_name"] = _safe_project_name(
            plan.get("project_name")
        )
        plan["files"] = safe_files

        return plan

    # =====================================================
    # SINGLE FILE / SCRIPT
    # =====================================================

    def write_script(
        self,
        request: str,
        language: str = "python",
        filename: str = "generated_script.py",
        destination: str | Path | None = None,
    ) -> CodingAgentResult:
        if destination is None:
            destination_path = PROJECTS_ROOT / "Scripts" / filename
        else:
            destination_path = Path(destination) / filename

        destination_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        prompt = f"""
{CODING_SYSTEM_PROMPT}

Write a complete {language} script for this user request:
{request}

Target filename:
{filename}

Requirements:
- Make it production-quality for the requested scope.
- Include error handling where appropriate.
- Include useful comments only where they improve maintainability.
- Do not use Markdown fences.
- Return ONLY the complete source code.
""".strip()

        try:
            content = _extract_code(
                self._chat(prompt, temperature=0.10)
            )

            if not content:
                raise ValueError("The coding agent returned an empty script.")

            destination_path.write_text(
                content,
                encoding="utf-8",
            )

            issues = self._validate_single_file(
                destination_path,
                destination_path.parent,
            )

            if issues:
                content = self._repair_file(
                    request,
                    {},
                    destination_path,
                    content,
                    issues[0],
                    {filename: content},
                )
                destination_path.write_text(
                    content,
                    encoding="utf-8",
                )
                issues = self._validate_single_file(
                    destination_path,
                    destination_path.parent,
                )

            if issues:
                return CodingAgentResult(
                    success=False,
                    message="The script was generated but still has validation errors.",
                    files_created=[str(destination_path)],
                    issues=issues,
                    model=self.model,
                )

            return CodingAgentResult(
                success=True,
                message=f"Script created: {destination_path}",
                files_created=[str(destination_path)],
                model=self.model,
            )

        except Exception as error:
            return CodingAgentResult(
                success=False,
                message=f"Coding agent error: {error}",
                model=self.model,
            )

    # =====================================================
    # MULTI-FILE PROJECT
    # =====================================================

    def build_project(
        self,
        request: str,
        project_name: str | None = None,
        open_project: bool | None = None,
        run_tests: bool = True,
    ) -> CodingAgentResult:
        project_dir = None

        try:
            set_coding_progress(
                stage="PLANNING",
                message="Analyzing the project request and planning the architecture...",
                model=self.model,
            )

            plan = self.plan_project(request)

            chosen_name = _safe_project_name(
                project_name or plan.get("project_name")
            )

            project_dir = _unique_project_dir(chosen_name)
            project_dir.mkdir(
                parents=True,
                exist_ok=False,
            )

            total_files = len(plan["files"])

            set_coding_progress(
                stage="CREATING PROJECT",
                message=f"Creating {chosen_name}...",
                project_dir=project_dir,
                files_done=0,
                files_total=total_files,
                model=self.model,
            )

            # Create the complete project tree first so the user can
            # immediately see the architecture appear in VS Code.
            safe_items = []

            for item in plan["files"]:
                relative = _safe_relative_path(
                    item.get("path")
                )

                if relative is None:
                    continue

                target = (
                    project_dir / relative
                ).resolve()

                root = project_dir.resolve()

                if root not in target.parents:
                    continue

                target.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                target.touch(
                    exist_ok=True
                )

                safe_items.append(
                    (
                        relative,
                        item,
                        target,
                    )
                )

            should_open = (
                self.auto_open
                if open_project is None
                else bool(open_project)
            )

            if should_open:
                set_coding_progress(
                    stage="OPENING VS CODE",
                    message="Opening the project in VS Code...",
                    project_dir=project_dir,
                    files_done=0,
                    files_total=len(safe_items),
                    model=self.model,
                )

                self.open_project(project_dir)

            project_files: dict[str, str] = {}
            created_paths: list[str] = []

            for index, (relative, item, target) in enumerate(
                safe_items,
                start=1,
            ):
                key = str(relative).replace("\\", "/")

                set_coding_progress(
                    stage="WRITING FILE",
                    message=f"Writing {key}...",
                    project_dir=project_dir,
                    current_file=key,
                    files_done=index - 1,
                    files_total=len(safe_items),
                    model=self.model,
                )

                content = self._chat_stream_to_file(
                    _build_file_prompt(
                        request,
                        plan,
                        key,
                        str(
                            item.get(
                                "purpose",
                                "Project file.",
                            )
                        ),
                        project_files,
                    ),
                    target,
                    temperature=0.12,
                )

                project_files[key] = content
                created_paths.append(key)

                set_coding_progress(
                    stage="FILE COMPLETE",
                    message=f"Finished {key}.",
                    project_dir=project_dir,
                    current_file=key,
                    files_done=index,
                    files_total=len(safe_items),
                    model=self.model,
                )

            if not created_paths:
                raise RuntimeError(
                    "The coding agent created no usable files."
                )

            set_coding_progress(
                stage="VALIDATING",
                message="Running syntax checks and project tests...",
                project_dir=project_dir,
                files_done=len(created_paths),
                files_total=len(created_paths),
                model=self.model,
            )

            issues = self.validate_project(
                project_dir,
                run_tests=run_tests,
            )

            for round_number in range(
                1,
                self.repair_rounds + 1,
            ):
                if not issues:
                    break

                issue = issues[0]
                target = project_dir / issue.path

                if not target.exists() or not target.is_file():
                    break

                current = target.read_text(
                    encoding="utf-8",
                    errors="replace",
                )

                set_coding_progress(
                    stage="REPAIRING",
                    message=(
                        f"Repairing {issue.path} "
                        f"(attempt {round_number}/{self.repair_rounds})..."
                    ),
                    project_dir=project_dir,
                    current_file=issue.path,
                    files_done=len(created_paths),
                    files_total=len(created_paths),
                    model=self.model,
                )

                repaired = self._repair_file(
                    request,
                    plan,
                    target,
                    current,
                    issue,
                    _read_project_files(project_dir),
                )

                target.write_text(
                    repaired,
                    encoding="utf-8",
                )

                issues = self.validate_project(
                    project_dir,
                    run_tests=run_tests,
                )

            if issues:
                set_coding_progress(
                    stage="NEEDS ATTENTION",
                    message=(
                        "The project was created, but validation still "
                        f"reports {len(issues)} issue(s)."
                    ),
                    project_dir=project_dir,
                    files_done=len(created_paths),
                    files_total=len(created_paths),
                    model=self.model,
                    done=True,
                    success=False,
                )

                return CodingAgentResult(
                    success=False,
                    message=(
                        "Project created, but validation still reports "
                        f"{len(issues)} issue(s)."
                    ),
                    project_dir=str(project_dir),
                    files_created=created_paths,
                    issues=issues,
                    model=self.model,
                )

            set_coding_progress(
                stage="COMPLETE",
                message=(
                    f"Finished. Created {len(created_paths)} files "
                    "and validation passed."
                ),
                project_dir=project_dir,
                files_done=len(created_paths),
                files_total=len(created_paths),
                model=self.model,
                done=True,
                success=True,
            )

            return CodingAgentResult(
                success=True,
                message=(
                    f"Project created successfully with "
                    f"{len(created_paths)} files."
                ),
                project_dir=str(project_dir),
                files_created=created_paths,
                model=self.model,
            )

        except Exception as error:
            set_coding_progress(
                stage="ERROR",
                message=f"Coding Agent error: {error}",
                project_dir=project_dir or "",
                model=self.model,
                done=True,
                success=False,
            )

            return CodingAgentResult(
                success=False,
                message=f"Coding agent project error: {error}",
                model=self.model,
            )

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate_project(
        self,
        project_dir: str | Path,
        run_tests: bool = True,
    ) -> list[ValidationIssue]:
        root = Path(project_dir)
        issues: list[ValidationIssue] = []

        if not root.exists():
            return [
                ValidationIssue(
                    path=".",
                    message="Project directory does not exist.",
                )
            ]

        # Python syntax validation.
        for path in root.rglob("*.py"):
            relative = str(path.relative_to(root)).replace("\\", "/")
            return_code, output = _run_process(
                [
                    sys.executable,
                    "-m",
                    "py_compile",
                    str(path),
                ],
                root,
                timeout=60,
            )

            if return_code != 0:
                issues.append(
                    ValidationIssue(
                        path=relative,
                        message="Python syntax validation failed.",
                        output=output,
                    )
                )

        # JavaScript syntax validation when Node is available.
        node = shutil.which("node")
        if node:
            for pattern in ("*.js", "*.mjs", "*.cjs"):
                for path in root.rglob(pattern):
                    relative = str(path.relative_to(root)).replace("\\", "/")
                    return_code, output = _run_process(
                        [node, "--check", str(path)],
                        root,
                        timeout=60,
                    )

                    if return_code != 0:
                        issues.append(
                            ValidationIssue(
                                path=relative,
                                message="JavaScript syntax validation failed.",
                                output=output,
                            )
                        )

        # Basic JSON validation.
        for path in root.rglob("*.json"):
            relative = str(path.relative_to(root)).replace("\\", "/")
            try:
                json.loads(
                    path.read_text(
                        encoding="utf-8"
                    )
                )
            except Exception as error:
                issues.append(
                    ValidationIssue(
                        path=relative,
                        message="JSON parsing failed.",
                        output=str(error),
                    )
                )

        if run_tests:
            pytest_available = self._pytest_available()
            test_files = list(root.rglob("test_*.py")) + list(root.rglob("*_test.py"))

            if pytest_available and test_files:
                return_code, output = _run_process(
                    [sys.executable, "-m", "pytest", "-q"],
                    root,
                    timeout=180,
                )

                if return_code != 0:
                    issues.append(
                        ValidationIssue(
                            path="tests",
                            message="Project tests failed.",
                            output=output,
                        )
                    )

        return issues

    @staticmethod
    def _pytest_available() -> bool:
        try:
            import pytest  # noqa: F401

            return True
        except Exception:
            return False

    def _validate_single_file(
        self,
        path: Path,
        project_root: Path,
    ) -> list[ValidationIssue]:
        suffix = path.suffix.lower()
        relative = str(path.relative_to(project_root)).replace("\\", "/")

        if suffix == ".py":
            return_code, output = _run_process(
                [
                    sys.executable,
                    "-m",
                    "py_compile",
                    str(path),
                ],
                project_root,
                timeout=60,
            )

            if return_code != 0:
                return [
                    ValidationIssue(
                        path=relative,
                        message="Python syntax validation failed.",
                        output=output,
                    )
                ]

        if suffix == ".json":
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except Exception as error:
                return [
                    ValidationIssue(
                        path=relative,
                        message="JSON parsing failed.",
                        output=str(error),
                    )
                ]

        return []

    # =====================================================
    # REPAIR
    # =====================================================

    def _repair_file(
        self,
        user_request: str,
        plan: dict[str, Any],
        path: Path,
        content: str,
        issue: ValidationIssue,
        project_files: dict[str, str],
    ) -> str:
        relative = str(path.name)
        try:
            relative = str(path.relative_to(path.parent.parent))
        except Exception:
            pass

        prompt = _build_repair_prompt(
            user_request,
            plan,
            relative.replace("\\", "/"),
            content,
            issue,
            project_files,
        )

        repaired = self._chat(
            prompt,
            temperature=0.05,
        )

        return _extract_code(repaired)

    # =====================================================
    # PROJECT OPENING
    # =====================================================

    @staticmethod
    def open_project(project_dir: str | Path) -> None:
        directory = Path(project_dir)
        code_command = shutil.which("code")

        if code_command is None and os.name == "nt":
            candidates = [
                os.path.expandvars(
                    r"%LOCALAPPDATA%\Programs\Microsoft VS Code\bin\code.cmd"
                ),
                os.path.expandvars(
                    r"%ProgramFiles%\Microsoft VS Code\bin\code.cmd"
                ),
            ]

            for candidate in candidates:
                if os.path.exists(candidate):
                    code_command = candidate
                    break

        try:
            if code_command:
                if str(code_command).lower().endswith(".cmd"):
                    subprocess.Popen(
                        [
                            "cmd.exe",
                            "/c",
                            code_command,
                            "--new-window",
                            str(directory),
                        ],
                        creationflags=(
                            subprocess.CREATE_NO_WINDOW
                            if os.name == "nt"
                            else 0
                        ),
                    )
                else:
                    subprocess.Popen(
                        [
                            code_command,
                            "--new-window",
                            str(directory),
                        ]
                    )

            elif os.name == "nt":
                os.startfile(str(directory))

            else:
                subprocess.Popen(
                    ["xdg-open", str(directory)]
                )

        except Exception as error:
            print(
                "Could not open coding project:",
                error,
            )

    # =====================================================
    # BACKWARD COMPATIBILITY
    # =====================================================

    def materialize_project_response(
        self,
        ai_response: str,
        open_project: bool | None = None,
    ) -> CodingAgentResult:
        """Accept the older full-JSON response format used by JARVIS."""
        try:
            plan = _extract_json(ai_response)
            project_name = _safe_project_name(
                plan.get("project_name")
            )

            files = plan.get("files")
            if not isinstance(files, list) or not files:
                raise ValueError("Project response contains no files.")

            project_dir = _unique_project_dir(project_name)
            project_dir.mkdir(parents=True, exist_ok=False)

            created: list[str] = []

            for item in files[:MAX_PROJECT_FILES]:
                if not isinstance(item, dict):
                    continue

                relative = _safe_relative_path(
                    item.get("path", "")
                )
                if relative is None:
                    continue

                destination = (project_dir / relative).resolve()
                root = project_dir.resolve()

                if root not in destination.parents:
                    continue

                content = str(item.get("content", ""))
                if len(content) > MAX_FILE_CHARS:
                    content = content[:MAX_FILE_CHARS]

                destination.parent.mkdir(
                    parents=True,
                    exist_ok=True,
                )
                destination.write_text(
                    content,
                    encoding="utf-8",
                )

                created.append(
                    str(relative).replace("\\", "/")
                )

            if not created:
                raise ValueError("No safe files were created.")

            issues = self.validate_project(
                project_dir,
                run_tests=True,
            )

            should_open = self.auto_open if open_project is None else bool(open_project)
            if should_open:
                self.open_project(project_dir)

            return CodingAgentResult(
                success=not issues,
                message=(
                    "Project created successfully."
                    if not issues
                    else "Project created, but validation found issues."
                ),
                project_dir=str(project_dir),
                files_created=created,
                issues=issues,
                model=self.model,
            )

        except Exception as error:
            return CodingAgentResult(
                success=False,
                message=f"Could not materialize project: {error}",
                model=self.model,
            )


# =========================================================
# MODULE-LEVEL API
# =========================================================


def create_project_from_response(ai_response: str):
    """Compatibility function for the existing JARVIS assistant."""
    agent = CodingAgent()
    result = agent.materialize_project_response(ai_response)
    return result.success, result.message


def create_project_from_prompt(
    prompt: str,
    project_name: str | None = None,
    open_project: bool = True,
):
    """Generate, validate, repair, and optionally open a project."""
    agent = CodingAgent(
        auto_open=open_project,
    )
    return agent.build_project(
        prompt,
        project_name=project_name,
        open_project=open_project,
        run_tests=True,
    )


def write_script_from_prompt(
    prompt: str,
    language: str = "python",
    filename: str = "generated_script.py",
    destination: str | Path | None = None,
):
    """Generate and validate a single script from a natural-language prompt."""
    agent = CodingAgent()
    return agent.write_script(
        prompt,
        language=language,
        filename=filename,
        destination=destination,
    )


__all__ = [
    "CodingAgent",
    "CodingAgentResult",
    "ValidationIssue",
    "PROJECTS_ROOT",
    "build_inline_code_prompt",
    "build_project_prompt",
    "create_project_from_response",
    "create_project_from_prompt",
    "write_script_from_prompt",
]
