import json
import os
import threading
from datetime import datetime

from core.paths import user_file


CONVERSATION_FILE = user_file(
    "conversation_history.json"
)

MAX_STORED_TURNS = 30
DEFAULT_CONTEXT_TURNS = 8
MAX_CONTEXT_CHARS = 12000

conversation_lock = threading.RLock()


def _default_data():
    return {
        "version": 1,
        "turns": []
    }


def _clean_text(value):
    return str(
        value or ""
    ).strip()


def _load_data():
    with conversation_lock:

        if not os.path.exists(
            CONVERSATION_FILE
        ):
            return _default_data()

        try:

            with open(
                CONVERSATION_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(
                    file
                )

            if not isinstance(
                data,
                dict
            ):
                return _default_data()

            turns = data.get(
                "turns",
                []
            )

            if not isinstance(
                turns,
                list
            ):
                turns = []

            cleaned_turns = []

            for turn in turns:

                if not isinstance(
                    turn,
                    dict
                ):
                    continue

                user = _clean_text(
                    turn.get(
                        "user",
                        ""
                    )
                )

                assistant = _clean_text(
                    turn.get(
                        "assistant",
                        ""
                    )
                )

                if not user and not assistant:
                    continue

                cleaned_turns.append(
                    {
                        "timestamp": str(
                            turn.get(
                                "timestamp",
                                ""
                            )
                        ),
                        "user": user,
                        "assistant": assistant,
                        "source": str(
                            turn.get(
                                "source",
                                "pc"
                            )
                        )
                    }
                )

            return {
                "version": 1,
                "turns": cleaned_turns[
                    -MAX_STORED_TURNS:
                ]
            }

        except Exception as error:

            print(
                "Conversation history load error:",
                error
            )

            return _default_data()


def _save_data(data):
    folder = os.path.dirname(
        CONVERSATION_FILE
    )

    os.makedirs(
        folder,
        exist_ok=True
    )

    temporary_file = (
        CONVERSATION_FILE
        + ".tmp"
    )

    try:

        with open(
            temporary_file,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )

        os.replace(
            temporary_file,
            CONVERSATION_FILE
        )

    except Exception:

        try:

            if os.path.exists(
                temporary_file
            ):
                os.remove(
                    temporary_file
                )

        except Exception:
            pass

        raise


def add_turn(
    user_message,
    assistant_message,
    source="pc"
):
    user_message = _clean_text(
        user_message
    )

    assistant_message = _clean_text(
        assistant_message
    )

    if not user_message and not assistant_message:
        return False

    with conversation_lock:

        data = _load_data()

        data["turns"].append(
            {
                "timestamp": datetime.now().isoformat(
                    timespec="seconds"
                ),
                "user": user_message,
                "assistant": assistant_message,
                "source": str(
                    source or "pc"
                )
            }
        )

        data["turns"] = data[
            "turns"
        ][
            -MAX_STORED_TURNS:
        ]

        try:

            _save_data(
                data
            )

            return True

        except Exception as error:

            print(
                "Conversation history save error:",
                error
            )

            return False


def get_recent_turns(
    limit=DEFAULT_CONTEXT_TURNS
):
    try:

        limit = int(
            limit
        )

    except Exception:

        limit = DEFAULT_CONTEXT_TURNS

    limit = max(
        1,
        min(
            limit,
            MAX_STORED_TURNS
        )
    )

    data = _load_data()

    return list(
        data.get(
            "turns",
            []
        )[
            -limit:
        ]
    )


def build_context(
    limit=DEFAULT_CONTEXT_TURNS,
    max_chars=MAX_CONTEXT_CHARS
):
    turns = get_recent_turns(
        limit
    )

    if not turns:
        return ""

    try:

        max_chars = int(
            max_chars
        )

    except Exception:

        max_chars = MAX_CONTEXT_CHARS

    max_chars = max(
        1000,
        max_chars
    )

    lines = [
        "RECENT CONVERSATION:"
    ]

    for turn in turns:

        user = _clean_text(
            turn.get(
                "user",
                ""
            )
        )

        assistant = _clean_text(
            turn.get(
                "assistant",
                ""
            )
        )

        if user:

            lines.append(
                f"User: {user}"
            )

        if assistant:

            lines.append(
                f"JARVIS: {assistant}"
            )

    context = "\n".join(
        lines
    )

    if len(context) > max_chars:

        context = context[
            -max_chars:
        ]

        first_newline = context.find(
            "\n"
        )

        if first_newline >= 0:

            context = context[
                first_newline + 1:
            ]

    return context.strip()


def get_last_user_message():
    turns = get_recent_turns(
        limit=1
    )

    if not turns:
        return ""

    return _clean_text(
        turns[-1].get(
            "user",
            ""
        )
    )


def get_last_assistant_message():
    turns = get_recent_turns(
        limit=1
    )

    if not turns:
        return ""

    return _clean_text(
        turns[-1].get(
            "assistant",
            ""
        )
    )


def clear_history():
    with conversation_lock:

        try:

            _save_data(
                _default_data()
            )

            return True

        except Exception as error:

            print(
                "Conversation history clear error:",
                error
            )

            return False


def get_history_count():
    data = _load_data()

    return len(
        data.get(
            "turns",
            []
        )
    )


def export_history():
    return _load_data()