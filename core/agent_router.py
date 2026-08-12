from core.coding_agent import (
    build_inline_code_prompt,
    build_project_prompt
)

from core.desktop_agent import (
    copy_selected_text,
    get_active_window_context
)


PASTE_PHRASES = (
    "paste it here",
    "paste here",
    "paste the answer here",
    "paste the summary here",
    "write it here",
    "put it here"
)


def _strip_jarvis_prefix(
    command
):
    text = command.strip()
    lower = text.lower()

    if lower.startswith(
        "jarvis "
    ):
        return text[
            7:
        ].strip()

    return text


def _wants_paste(
    command_lower
):
    return any(
        phrase in command_lower
        for phrase in PASTE_PHRASES
    )


def _selection_prompt(
    command,
    selected_text
):
    lower = command.lower()

    if (
        "fix this code" in lower
        or "fix the code" in lower
    ):
        instruction = (
            "Fix the selected code. "
            "Return only the corrected code, "
            "with no Markdown fences "
            "or explanation."
        )

    elif "add comments" in lower:
        instruction = (
            "Add useful comments to the "
            "selected code. Return only "
            "the updated code, with no "
            "Markdown fences or explanation."
        )

    elif (
        "fix grammar" in lower
        or "correct grammar" in lower
    ):
        instruction = (
            "Correct the grammar and wording "
            "while preserving the meaning. "
            "Return only the revised text."
        )

    elif (
        "make this shorter" in lower
        or "shorten this" in lower
    ):
        instruction = (
            "Make the selected text shorter "
            "while preserving its important "
            "meaning. Return only the "
            "revised text."
        )

    elif "rewrite this" in lower:
        instruction = (
            "Rewrite the selected text "
            "clearly and naturally. "
            "Return only the rewritten text."
        )

    elif "translate this" in lower:
        instruction = (
            f"Follow this translation request: "
            f"{command}. "
            "Return only the translated text."
        )

    elif "summarize" in lower:
        instruction = (
            "Summarize the selected text "
            "accurately and concisely. "
            "Return only the summary."
        )

    else:
        instruction = (
            "Explain the selected text "
            "clearly and concisely."
        )

    return f"""
{instruction}

Selected content:
---
{selected_text}
---
""".strip()


def build_agent_request(
    raw_command
):
    command = _strip_jarvis_prefix(
        raw_command
    )

    lower = (
        command
        .lower()
        .strip()
    )

    # =========================
    # LITERAL TYPE
    # =========================

    if lower.startswith(
        "type "
    ):
        text = command[
            5:
        ].strip()

        if not text:
            return {
                "kind": "message",
                "message": (
                    "Tell me what you would "
                    "like me to type, sir."
                )
            }

        return {
            "kind": "literal_paste",
            "text": text
        }

    # =========================
    # MULTI-FILE PROJECT
    # =========================

    project_markers = (
        "create a coding project",
        "create a project",
        "build a project",
        "make a project",
        "build an app",
        "create an app",
        "make an app"
    )

    coding_words = (
        "program",
        "code",
        "app",
        "website",
        "python",
        "javascript",
        "html"
    )

    project_requested = any(
        marker in lower
        for marker
        in project_markers
    )

    project_requested = (
        project_requested
        or (
            "necessary files"
            in lower
            and any(
                word in lower
                for word
                in coding_words
            )
        )
    )

    if project_requested:
        return {
            "kind": "project",
            "prompt": (
                build_project_prompt(
                    command
                )
            )
        }

    # =========================
    # QUICK CODE
    # =========================

    code_markers = (
        "write a program",
        "write code",
        "generate code",
        "write a python",
        "write a function",
        "create a function",
        "code a "
    )

    if any(
        marker in lower
        for marker
        in code_markers
    ):
        return {
            "kind": "paste_ai",

            "prompt": (
                build_inline_code_prompt(
                    command,
                    get_active_window_context()
                )
            ),

            "success_message": (
                "I wrote the code "
                "at your cursor, sir."
            )
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
        "add comments"
    )

    if any(
        marker in lower
        for marker
        in selection_markers
    ):
        selected = (
            copy_selected_text()
        )

        if not selected:
            return {
                "kind": "message",

                "message": (
                    "I couldn't detect selected "
                    "text. Highlight the text "
                    "or code first, then ask "
                    "me again, sir."
                )
            }

        prompt = _selection_prompt(
            command,
            selected
        )

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
                "add comments"
            )
        )

        if (
            replace_by_default
            or _wants_paste(
                lower
            )
        ):
            return {
                "kind": "paste_ai",
                "prompt": prompt,
                "success_message": (
                    "Done, sir."
                )
            }

        return {
            "kind": "speak_ai",
            "prompt": prompt
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
        "create a summary"
    )

    if (
        _wants_paste(
            lower
        )
        and any(
            marker in lower
            for marker
            in writing_markers
        )
    ):
        prompt = f"""
Create the content requested by the user below.

Return ONLY the finished text that should
be pasted into their document.

Do not add an introduction about what
you are doing.

Use plain text unless the user specifically
asks for bullets or another format.

User request:
{command}
""".strip()

        return {
            "kind": "paste_ai",
            "prompt": prompt,

            "success_message": (
                "I pasted it at "
                "your cursor, sir."
            )
        }

    return None