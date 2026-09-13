from __future__ import annotations

import re
import threading
import uuid

from dataclasses import dataclass
from time import monotonic
from typing import Callable, Optional


# =========================================================
# ACTION TYPES
# =========================================================

ActionCallback = Callable[[], str]


@dataclass
class SuggestedAction:
    action_id: str
    label: str
    description: str
    callback: ActionCallback
    requires_confirmation: bool = False


@dataclass
class PendingAction:
    action_id: str
    label: str
    description: str
    callback: ActionCallback
    created_at: float
    expires_after: float = 120.0


# =========================================================
# STATE
# =========================================================

_lock = threading.RLock()

_suggestions: list[SuggestedAction] = []

_pending_action: Optional[
    PendingAction
] = None


# =========================================================
# CREATE ACTION
# =========================================================

def create_action(
    label: str,
    callback: ActionCallback,
    description: str = "",
    requires_confirmation: bool = False,
) -> SuggestedAction:

    return SuggestedAction(
        action_id=uuid.uuid4().hex,
        label=label.strip(),
        description=description.strip(),
        callback=callback,
        requires_confirmation=requires_confirmation,
    )


# =========================================================
# SUGGESTIONS
# =========================================================

def set_suggestions(
    actions: list[SuggestedAction],
) -> None:

    global _suggestions

    with _lock:

        _suggestions = (
            actions[:5]
        )


def clear_suggestions() -> None:

    global _suggestions

    with _lock:
        _suggestions = []


def get_suggestions() -> list[dict]:

    with _lock:

        return [
            {
                "id": action.action_id,
                "label": action.label,
                "description": action.description,
                "requires_confirmation":
                    action.requires_confirmation,
            }
            for action in _suggestions
        ]


# =========================================================
# PENDING CONFIRMATION
# =========================================================

def _pending_is_expired(
    action: PendingAction,
) -> bool:

    age = (
        monotonic()
        - action.created_at
    )

    return (
        age
        > action.expires_after
    )


def get_pending_action() -> Optional[dict]:

    global _pending_action

    with _lock:

        if _pending_action is None:
            return None

        if _pending_is_expired(
            _pending_action
        ):
            _pending_action = None
            return None

        return {
            "id":
                _pending_action.action_id,

            "label":
                _pending_action.label,

            "description":
                _pending_action.description,
        }


def request_confirmation(
    label: str,
    description: str,
    callback: ActionCallback,
    expires_after: float = 120.0,
) -> str:

    global _pending_action

    with _lock:

        _pending_action = PendingAction(
            action_id=uuid.uuid4().hex,
            label=label.strip(),
            description=description.strip(),
            callback=callback,
            created_at=monotonic(),
            expires_after=expires_after,
        )

    if description:

        return (
            f"{description} "
            "Want me to do it?"
        )

    return (
        f"Want me to {label}?"
    )


# =========================================================
# EXECUTE PENDING
# =========================================================

def confirm_pending_action() -> str:

    global _pending_action

    with _lock:

        action = _pending_action

        if action is None:
            return (
                "There's nothing waiting "
                "for confirmation."
            )

        if _pending_is_expired(
            action
        ):
            _pending_action = None

            return (
                "That action expired. "
                "Ask me again if you still "
                "want to do it."
            )

        _pending_action = None

    try:

        result = action.callback()

        if result:
            return str(
                result
            )

        return (
            f"Done. {action.label}."
        )

    except Exception as error:

        return (
            "I couldn't complete that action: "
            f"{error}"
        )


def cancel_pending_action() -> str:

    global _pending_action

    with _lock:

        action = _pending_action
        _pending_action = None

    if action is None:

        return (
            "There's nothing waiting "
            "to cancel."
        )

    return (
        "Cancelled."
    )


# =========================================================
# RUN SUGGESTION
# =========================================================

def run_suggestion(
    index: int,
) -> str:

    with _lock:

        if not _suggestions:

            return (
                "I don't have any active "
                "suggestions right now."
            )

        if (
            index < 0
            or index >= len(
                _suggestions
            )
        ):
            return (
                "That suggestion isn't available."
            )

        action = (
            _suggestions[
                index
            ]
        )

    if action.requires_confirmation:

        return request_confirmation(
            label=action.label,
            description=(
                action.description
                or action.label
            ),
            callback=action.callback,
        )

    try:

        result = (
            action.callback()
        )

        if result:
            return str(
                result
            )

        return (
            f"Done. {action.label}."
        )

    except Exception as error:

        return (
            "I couldn't complete that action: "
            f"{error}"
        )


# =========================================================
# SELECTION PARSER
# =========================================================

def _suggestion_number(
    command: str,
) -> Optional[int]:

    text = (
        command
        .lower()
        .strip()
    )

    words = {
        "first": 0,
        "1st": 0,
        "one": 0,
        "second": 1,
        "2nd": 1,
        "two": 1,
        "third": 2,
        "3rd": 2,
        "three": 2,
        "fourth": 3,
        "4th": 3,
        "four": 3,
        "fifth": 4,
        "5th": 4,
        "five": 4,
    }

    for word, index in words.items():

        if re.search(
            rf"\b{re.escape(word)}\b",
            text,
        ):
            return index

    number_match = re.search(
        r"\b(?:option|choice|suggestion)\s+([1-5])\b",
        text,
    )

    if number_match:

        return (
            int(
                number_match.group(
                    1
                )
            )
            - 1
        )

    return None


# =========================================================
# NATURAL ACTION COMMANDS
# =========================================================

def handle_action_command(
    command: str,
) -> Optional[str]:

    text = (
        str(command)
        .lower()
        .strip()
    )

    if not text:
        return None


    # -----------------------------------------------------
    # CONFIRMATION
    # -----------------------------------------------------

    confirm_phrases = {
        "yes",
        "yeah",
        "yep",
        "sure",
        "do it",
        "go ahead",
        "confirm",
        "yes do it",
        "yeah do it",
        "please do",
    }

    if (
        text in confirm_phrases
        and get_pending_action()
        is not None
    ):
        return confirm_pending_action()


    # -----------------------------------------------------
    # CANCEL
    # -----------------------------------------------------

    cancel_phrases = {
        "no",
        "nope",
        "cancel",
        "never mind",
        "nevermind",
        "don't do it",
        "dont do it",
        "stop",
    }

    if (
        text in cancel_phrases
        and get_pending_action()
        is not None
    ):
        return cancel_pending_action()


    # -----------------------------------------------------
    # SUGGESTION SELECTION
    # -----------------------------------------------------

    selection_phrases = (
        "do the",
        "pick the",
        "choose the",
        "use the",
        "open the",
        "select the",
        "option ",
        "choice ",
        "suggestion ",
    )

    if any(
        phrase in text
        for phrase in selection_phrases
    ):

        index = (
            _suggestion_number(
                text
            )
        )

        if index is not None:

            return run_suggestion(
                index
            )

    return None


# =========================================================
# UI/API PAYLOAD
# =========================================================

def get_action_state() -> dict:

    return {
        "pending":
            get_pending_action(),

        "suggestions":
            get_suggestions(),
    }