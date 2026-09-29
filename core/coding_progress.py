import json
import os
import time

from core.paths import user_file


CODING_STATUS_FILE = user_file("coding_agent_status.json")


def _status_payload(**values):
    payload = {
        "active": True,
        "timestamp": time.time(),
        "stage": "WORKING",
        "message": "Coding Agent is working...",
        "project_dir": "",
        "current_file": "",
        "files_done": 0,
        "files_total": 0,
        "model": "",
        "done": False,
        "success": None,
    }
    payload.update(values)
    return payload


def set_coding_progress(
    stage="WORKING",
    message="Coding Agent is working...",
    project_dir="",
    current_file="",
    files_done=0,
    files_total=0,
    model="",
    done=False,
    success=None,
):
    payload = _status_payload(
        stage=str(stage),
        message=str(message),
        project_dir=str(project_dir or ""),
        current_file=str(current_file or ""),
        files_done=int(files_done),
        files_total=int(files_total),
        model=str(model or ""),
        done=bool(done),
        success=success,
    )

    path = CODING_STATUS_FILE
    directory = os.path.dirname(path)

    try:
        os.makedirs(directory, exist_ok=True)

        temporary = f"{path}.tmp"

        with open(
            temporary,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                payload,
                file,
                indent=2,
            )

        os.replace(
            temporary,
            path,
        )

    except Exception as error:
        print(
            "Coding progress write error:",
            error,
        )


def read_coding_progress():
    path = CODING_STATUS_FILE

    try:
        if not os.path.exists(path):
            return None

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        if not isinstance(data, dict):
            return None

        return data

    except Exception:
        return None


def clear_coding_progress():
    try:
        if os.path.exists(CODING_STATUS_FILE):
            os.remove(CODING_STATUS_FILE)
    except OSError:
        pass


__all__ = [
    "CODING_STATUS_FILE",
    "set_coding_progress",
    "read_coding_progress",
    "clear_coding_progress",
]
