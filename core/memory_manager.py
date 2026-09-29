import json
import os
import threading

from core.paths import (
    get_app_dir,
    user_file
)


MEMORY_FILE = user_file(
    "memory.json"
)

LEGACY_MEMORY_FILE = os.path.join(
    get_app_dir(),
    "memory",
    "memory.json"
)

memory_lock = threading.RLock()


def _default_memory():
    return {
        "version": 2,
        "user": {},
        "history": []
    }


def _normalize_memory(memory):
    if not isinstance(memory, dict):
        return _default_memory()

    user_data = memory.get(
        "user",
        {}
    )

    history = memory.get(
        "history",
        []
    )

    if not isinstance(
        user_data,
        dict
    ):
        user_data = {}

    if not isinstance(
        history,
        list
    ):
        history = []

    return {
        "version": 2,
        "user": user_data,
        "history": history
    }


def _migrate_legacy_memory():
    if os.path.exists(
        MEMORY_FILE
    ):
        return

    if not os.path.exists(
        LEGACY_MEMORY_FILE
    ):
        return

    try:

        with open(
            LEGACY_MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            legacy_memory = json.load(
                file
            )

        normalized = _normalize_memory(
            legacy_memory
        )

        folder = os.path.dirname(
            MEMORY_FILE
        )

        os.makedirs(
            folder,
            exist_ok=True
        )

        with open(
            MEMORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                normalized,
                file,
                indent=4,
                ensure_ascii=False
            )

        print(
            "Migrated JARVIS memory to:",
            MEMORY_FILE
        )

    except Exception as error:

        print(
            "Memory migration error:",
            error
        )


def load_memory():
    with memory_lock:

        _migrate_legacy_memory()

        if not os.path.exists(
            MEMORY_FILE
        ):
            return _default_memory()

        try:

            with open(
                MEMORY_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                memory = json.load(
                    file
                )

            return _normalize_memory(
                memory
            )

        except Exception as error:

            print(
                "Memory load error:",
                error
            )

            return _default_memory()


def save_memory(memory):
    memory = _normalize_memory(
        memory
    )

    with memory_lock:

        folder = os.path.dirname(
            MEMORY_FILE
        )

        os.makedirs(
            folder,
            exist_ok=True
        )

        temporary_file = (
            MEMORY_FILE
            + ".tmp"
        )

        try:

            with open(
                temporary_file,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    memory,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            os.replace(
                temporary_file,
                MEMORY_FILE
            )

            return True

        except Exception as error:

            print(
                "Memory save error:",
                error
            )

            try:

                if os.path.exists(
                    temporary_file
                ):
                    os.remove(
                        temporary_file
                    )

            except Exception:
                pass

            return False


def remember(
    key,
    value
):
    key = str(
        key
        or ""
    ).strip().lower()

    if not key:
        return False

    value = str(
        value
        or ""
    ).strip()

    if not value:
        return False

    memory = load_memory()

    memory["user"][key] = value

    return save_memory(
        memory
    )


def recall(
    key
):
    key = str(
        key
        or ""
    ).strip().lower()

    if not key:
        return None

    memory = load_memory()

    return memory["user"].get(
        key,
        None
    )


def forget(
    key
):
    key = str(
        key
        or ""
    ).strip().lower()

    if not key:
        return False

    memory = load_memory()

    if key not in memory["user"]:
        return False

    del memory["user"][key]

    return save_memory(
        memory
    )


def list_memories():
    memory = load_memory()

    return dict(
        memory.get(
            "user",
            {}
        )
    )


def get_memory_context():
    memories = list_memories()

    if not memories:
        return ""

    lines = [
        "KNOWN USER INFORMATION:"
    ]

    for key, value in memories.items():

        lines.append(
            f"- {key}: {value}"
        )

    return "\n".join(
        lines
    )