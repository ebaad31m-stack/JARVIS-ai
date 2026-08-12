import json
import os
import re
import shutil
import subprocess

from pathlib import (
    Path,
    PurePosixPath
)


PROJECTS_ROOT = (
    Path.home()
    / "Documents"
    / "JARVIS Projects"
)

MAX_PROJECT_FILES = 40
MAX_FILE_CHARS = 500_000


def build_inline_code_prompt(
    request,
    window_context
):
    return f"""
You are JARVIS acting as a coding assistant.

The user wants code inserted directly at the
current cursor position.

{window_context}

User request:
{request}

Return ONLY the code or file content that should
be pasted into the editor.

Do not use Markdown code fences.
Do not explain the code before or after it.
Keep the result complete enough to satisfy
the request.
""".strip()


def build_project_prompt(
    request
):
    return f"""
You are JARVIS creating a small software project
for the user.

User request:
{request}

Return ONLY valid JSON in exactly this shape:

{{
    "project_name": "short_project_name",
    "files": [
        {{
            "path": "relative/path/to/file.ext",
            "content": "complete file contents"
        }}
    ]
}}

Rules:

- Create only the files genuinely needed.
- Use relative paths only.
- Never use .. path traversal.
- Do not include binary files.
- Do not include Markdown fences.
- Do not include shell commands outside a file.
- Do not execute anything.
- Keep the project reasonably small.
""".strip()


def _extract_json(
    text
):
    text = text.strip()

    if text.startswith(
        "```"
    ):
        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(
            r"\s*```$",
            "",
            text
        )

    start = text.find(
        "{"
    )

    end = text.rfind(
        "}"
    )

    if (
        start == -1
        or end == -1
        or end <= start
    ):
        raise ValueError(
            "AI did not return "
            "a JSON project plan."
        )

    return json.loads(
        text[
            start:end + 1
        ]
    )


def _safe_project_name(
    name
):
    name = str(
        name
        or "jarvis_project"
    ).strip()

    name = re.sub(
        r"[^A-Za-z0-9._ -]+",
        "",
        name
    )

    name = re.sub(
        r"\s+",
        "_",
        name
    )

    name = name.strip(
        "._-"
    )

    return (
        name
        or "jarvis_project"
    )[:60]


def _unique_project_dir(
    project_name
):
    PROJECTS_ROOT.mkdir(
        parents=True,
        exist_ok=True
    )

    base = (
        PROJECTS_ROOT
        / project_name
    )

    if not base.exists():
        return base

    index = 2

    while True:
        candidate = (
            PROJECTS_ROOT
            / f"{project_name}_{index}"
        )

        if not candidate.exists():
            return candidate

        index += 1


def _safe_relative_path(
    value
):
    value = (
        str(value)
        .replace(
            "\\",
            "/"
        )
        .strip()
    )

    pure = PurePosixPath(
        value
    )

    if (
        pure.is_absolute()
        or ".." in pure.parts
    ):
        return None

    cleaned_parts = [
        part
        for part in pure.parts
        if part not in (
            "",
            "."
        )
    ]

    if not cleaned_parts:
        return None

    return Path(
        *cleaned_parts
    )


def _open_project(
    project_dir
):
    code_command = shutil.which(
        "code"
    )

    try:
        if code_command:
            subprocess.Popen(
                [
                    code_command,
                    str(project_dir)
                ]
            )

        else:
            os.startfile(
                str(project_dir)
            )

    except Exception as error:
        print(
            "Could not open "
            "generated project:",
            error
        )


def create_project_from_response(
    ai_response
):
    try:
        plan = _extract_json(
            ai_response
        )

    except Exception as error:
        return (
            False,
            "I couldn't understand the "
            f"project plan. {error}"
        )

    project_name = (
        _safe_project_name(
            plan.get(
                "project_name"
            )
        )
    )

    files = plan.get(
        "files"
    )

    if (
        not isinstance(
            files,
            list
        )
        or not files
    ):
        return (
            False,
            "The AI project plan "
            "did not contain any files."
        )

    project_dir = (
        _unique_project_dir(
            project_name
        )
    )

    project_dir.mkdir(
        parents=True,
        exist_ok=False
    )

    project_root = (
        project_dir.resolve()
    )

    created = 0

    try:
        for item in files[
            :MAX_PROJECT_FILES
        ]:
            if not isinstance(
                item,
                dict
            ):
                continue

            relative = (
                _safe_relative_path(
                    item.get(
                        "path",
                        ""
                    )
                )
            )

            if relative is None:
                continue

            content = str(
                item.get(
                    "content",
                    ""
                )
            )

            if (
                len(content)
                > MAX_FILE_CHARS
            ):
                content = content[
                    :MAX_FILE_CHARS
                ]

            destination = (
                project_dir
                / relative
            ).resolve()

            if (
                destination
                != project_root
                and project_root
                not in destination.parents
            ):
                continue

            destination.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            destination.write_text(
                content,
                encoding="utf-8"
            )

            created += 1

    except Exception as error:
        return (
            False,
            "Project creation stopped "
            f"because of an error: {error}"
        )

    if created == 0:
        return (
            False,
            "The project plan did not "
            "contain any safe files to create."
        )

    _open_project(
        project_dir
    )

    return (
        True,
        f"Project created with "
        f"{created} files. "
        f"I opened "
        f"{project_dir.name} "
        f"for you, sir."
    )