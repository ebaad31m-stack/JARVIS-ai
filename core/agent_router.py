from core.coding_agent import (
    build_inline_code_prompt,
    build_project_prompt,
)

from core.desktop_agent import (
    copy_selected_text,
    get_active_window_context,
)


PASTE_PHRASES = (
    "paste it here",
    "paste here",
    "paste the answer here",
    "paste the summary here",
    "write it here",
    "put it here",
)


PROJECT_MARKERS = (
    "create a coding project",
    "create a project",
    "build a project",
    "make a project",
    "build an app",
    "build me an app",
    "create an app",
    "make an app",
    "build a website",
    "build me a website",
    "create a website",
    "make a website",
    "develop an app",
    "develop a website",
    "develop a program",
    "make me a program",
    "build me a program",
    "create me a program",
)

PROJECT_WORDS = (
    "project",
    "app",
    "application",
    "website",
    "program",
    "game",
)

CODING_WORDS = (
    "code",
    "coding",
    "script",
    "python",
    "javascript",
    "typescript",
    "html",
    "css",
    "java",
    "c++",
    "c#",
    "sql",
    "program",
    "app",
    "website",
)

SCRIPT_MARKERS = (
    "write a script",
    "write me a script",
    "create a script",
    "make a script",
    "generate a script",
    "write code",
    "generate code",
    "write a program",
    "write me a program",
    "write a python",
    "write me a python",
    "write a javascript",
    "write me a javascript",
    "write a function",
    "create a function",
    "code a ",
    "code me ",
    "make me a script",
)

CODING_AGENT_MARKERS = (
    "coding agent",
    "code agent",
    "developer agent",
    "software engineer",
    "senior programmer",
    "programming agent",
)


def _strip_jarvis_prefix(command):
    text = str(command or "").strip()
    lower = text.lower()

    for prefix in (
        "jarvis ",
        "jarvis,",
        "jarvis:",
        "jarvis-",
    ):
        if lower.startswith(prefix):
            return text[len(prefix):].strip()

    return text


def _wants_paste(command_lower):
    return any(
        phrase in command_lower
        for phrase in PASTE_PHRASES
    )


def _looks_like_coding_request(lower):
    return any(
        marker in lower
        for marker in CODING_WORDS
    )


def _selection_prompt(command, selected_text):
    lower = command.lower()

    if "fix this code" in lower or "fix the code" in lower:
        instruction = (
            "Fix the selected code. Return only the corrected code, "
            "with no Markdown fences or explanation."
        )
    elif "add comments" in lower:
        instruction = (
            "Add useful comments to the selected code. Return only "
            "the updated code, with no Markdown fences or explanation."
        )
    elif "fix grammar" in lower or "correct grammar" in lower:
        instruction = (
            "Correct the grammar and wording while preserving the meaning. "
            "Return only the revised text."
        )
    elif "make this shorter" in lower or "shorten this" in lower:
        instruction = (
            "Make the selected text shorter while preserving its important "
            "meaning. Return only the revised text."
        )
    elif "rewrite this" in lower:
        instruction = (
            "Rewrite the selected text clearly and naturally. "
            "Return only the rewritten text."
        )
    elif "translate this" in lower:
        instruction = (
            f"Follow this translation request: {command}. "
            "Return only the translated text."
        )
    elif "summarize" in lower:
        instruction = (
            "Summarize the selected text accurately and concisely. "
            "Return only the summary."
        )
    else:
        instruction = "Explain the selected text clearly and concisely."

    return f"""
{instruction}

Selected content:
---
{selected_text}
---
""".strip()


def build_agent_request(raw_command):
    command = _strip_jarvis_prefix(raw_command)
    lower = command.lower().strip()

    if not lower:
        return None

    # =========================
    # LITERAL TYPE
    # =========================
    if lower.startswith("type "):
        text = command[5:].strip()

        if not text:
            return {
                "kind": "message",
                "message": "Tell me what you would like me to type, sir.",
            }

        return {
            "kind": "literal_paste",
            "text": text,
        }

    # =========================
    # DEDICATED CODING AGENT
    # =========================
    explicit_agent = any(
        marker in lower
        for marker in CODING_AGENT_MARKERS
    )

    project_requested = any(
        marker in lower
        for marker in PROJECT_MARKERS
    )

    project_requested = (
        project_requested
        or (
            "necessary files" in lower
            and _looks_like_coding_request(lower)
        )
        or (
            "multi file" in lower
            and _looks_like_coding_request(lower)
        )
        or (
            "multiple files" in lower
            and _looks_like_coding_request(lower)
        )
    )

    # Be much more natural about project requests.
    # Examples that should become a REAL Coding Agent task:
    # "build me a python game"
    # "make me a website with login"
    # "create a javascript app"
    # "develop a desktop program"
    build_verbs = (
        "build ",
        "build me ",
        "create ",
        "create me ",
        "make ",
        "make me ",
        "develop ",
        "develop me ",
        "generate ",
    )

    project_like = any(
        word in lower
        for word in PROJECT_WORDS
    )

    coding_like = _looks_like_coding_request(lower)

    direct_build_request = any(
        lower.startswith(verb)
        for verb in build_verbs
    ) or any(
        phrase in lower
        for phrase in (
            "can you build ",
            "could you build ",
            "please build ",
            "i want you to build ",
            "i want you to create ",
            "i want you to make ",
            "can you create ",
            "can you make ",
            "please create ",
            "please make ",
        )
    )

    informational_build_question = any(
        phrase in lower
        for phrase in (
            "what should i use to build",
            "what should i use to create",
            "what should i use to make",
            "what do i use to build",
            "what do i use to create",
            "what can i use to build",
            "what can i use to create",
            "how should i build",
            "how do i build",
            "how can i build",
        )
    )

    natural_project_request = (
        project_like
        and coding_like
        and direct_build_request
        and not informational_build_question
    )

    if natural_project_request:
        project_requested = True

    # Questions asking for advice should stay with normal JARVIS AI.
    if informational_build_question and not explicit_agent:
        project_requested = False

    if explicit_agent and project_like:
        project_requested = True

    if project_requested:
        return {
            "kind": "coding_project",
            "prompt": command,
            "planning_prompt": build_project_prompt(command),
        }

    # =========================
    # SINGLE SCRIPT / PROGRAM
    # =========================
    script_requested = any(
        marker in lower
        for marker in SCRIPT_MARKERS
    )

    if explicit_agent or script_requested:
        return {
            "kind": "coding_script",
            "prompt": command,
            "context": get_active_window_context(),
        }

    # =========================
    # SELECTED TEXT / CODE
    # =========================
    selection_markers = (
        "summarize this",
        "summarize the selection",
        "summarize selected",
        "rewrite this",
        "fix grammar",
        "correct grammar",
        "make this shorter",
        "shorten this",
        "translate this",
        "explain this",
        "explain the selection",
        "fix this code",
        "fix the code",
        "add comments",
    )

    if any(marker in lower for marker in selection_markers):
        selected = copy_selected_text()

        if not selected:
            return {
                "kind": "message",
                "message": (
                    "I couldn't detect selected text. Highlight the text "
                    "or code first, then ask me again, sir."
                ),
            }

        prompt = _selection_prompt(command, selected)

        replace_by_default = any(
            marker in lower
            for marker in (
                "rewrite this",
                "fix grammar",
                "correct grammar",
                "make this shorter",
                "shorten this",
                "translate this",
                "fix this code",
                "fix the code",
                "add comments",
            )
        )

        if replace_by_default or _wants_paste(lower):
            return {
                "kind": "paste_ai",
                "prompt": prompt,
                "success_message": "Done, sir.",
            }

        return {
            "kind": "speak_ai",
            "prompt": prompt,
        }

    # =========================
    # GENERAL WRITING
    # =========================
    writing_markers = (
        "summarize ",
        "write about ",
        "write a summary",
        "write a paragraph",
        "write an essay",
        "draft ",
        "create a summary",
    )

    if (
        _wants_paste(lower)
        and any(marker in lower for marker in writing_markers)
    ):
        prompt = f"""
Create the content requested by the user below.

Return ONLY the finished text that should be pasted into their document.

Do not add an introduction about what you are doing.

Use plain text unless the user specifically asks for bullets or another format.

User request:
{command}
""".strip()

        return {
            "kind": "paste_ai",
            "prompt": prompt,
            "success_message": "I pasted it at your cursor, sir.",
        }

    return None
