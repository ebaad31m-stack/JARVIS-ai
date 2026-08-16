import json
import os
import secrets
import socket

from core.paths import user_file


REMOTE_SETTINGS_FILE = user_file(
    "remote_settings.json"
)


DEFAULT_REMOTE_SETTINGS = {
    "enabled": True,
    "host": "0.0.0.0",
    "port": 8765,
    "pairing_token": "",
}


# =========================================================
# INTERNAL SAVE
# =========================================================

def _write_settings(
    settings
):
    folder = os.path.dirname(
        REMOTE_SETTINGS_FILE
    )

    if folder:
        os.makedirs(
            folder,
            exist_ok=True,
        )

    with open(
        REMOTE_SETTINGS_FILE,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            settings,
            file,
            indent=4,
        )


# =========================================================
# PORT
# =========================================================

def _safe_port(
    value
):
    try:
        port = int(
            value
        )

    except Exception:
        port = 8765

    if not (
        1024
        <= port
        <= 65535
    ):
        port = 8765

    return port


# =========================================================
# LOAD
# =========================================================

def load_remote_settings():
    settings = (
        DEFAULT_REMOTE_SETTINGS.copy()
    )

    changed = False

    if os.path.exists(
        REMOTE_SETTINGS_FILE
    ):
        try:
            with open(
                REMOTE_SETTINGS_FILE,
                "r",
                encoding="utf-8",
            ) as file:
                saved = json.load(
                    file
                )

            if isinstance(
                saved,
                dict,
            ):
                settings.update(
                    saved
                )

        except Exception as error:
            print(
                "Remote settings load error:",
                error,
            )

    else:
        changed = True

    settings[
        "enabled"
    ] = bool(
        settings.get(
            "enabled",
            True,
        )
    )

    settings[
        "host"
    ] = str(
        settings.get(
            "host",
            "0.0.0.0",
        )
    ).strip() or "0.0.0.0"

    settings[
        "port"
    ] = _safe_port(
        settings.get(
            "port",
            8765,
        )
    )

    token = str(
        settings.get(
            "pairing_token",
            "",
        )
    ).strip()

    # Generate token on first use.
    if len(
        token
    ) < 16:
        token = secrets.token_hex(
            16
        )

        settings[
            "pairing_token"
        ] = token

        changed = True

    if changed:
        try:
            _write_settings(
                settings
            )

        except Exception as error:
            print(
                "Remote settings save error:",
                error,
            )

    return settings


# =========================================================
# SAVE
# =========================================================

def save_remote_settings(
    new_settings
):
    current = (
        load_remote_settings()
    )

    if isinstance(
        new_settings,
        dict,
    ):
        current.update(
            new_settings
        )

    current[
        "enabled"
    ] = bool(
        current.get(
            "enabled",
            True,
        )
    )

    current[
        "host"
    ] = str(
        current.get(
            "host",
            "0.0.0.0",
        )
    ).strip() or "0.0.0.0"

    current[
        "port"
    ] = _safe_port(
        current.get(
            "port",
            8765,
        )
    )

    token = str(
        current.get(
            "pairing_token",
            "",
        )
    ).strip()

    if len(
        token
    ) < 16:
        current[
            "pairing_token"
        ] = secrets.token_hex(
            16
        )

    _write_settings(
        current
    )

    return current


# =========================================================
# REGENERATE PAIRING TOKEN
# =========================================================

def regenerate_pairing_token():
    settings = (
        load_remote_settings()
    )

    settings[
        "pairing_token"
    ] = secrets.token_hex(
        16
    )

    _write_settings(
        settings
    )

    return settings[
        "pairing_token"
    ]


# =========================================================
# LOCAL IP
# =========================================================

def get_local_ip():
    sock = None

    try:
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM,
        )

        # No actual data needs to be sent.
        # This lets Windows tell us which
        # network interface would be used.
        sock.connect(
            (
                "8.8.8.8",
                80,
            )
        )

        address = (
            sock.getsockname()[
                0
            ]
        )

        if address:
            return address

    except Exception:
        pass

    finally:
        if sock is not None:
            try:
                sock.close()

            except Exception:
                pass

    try:
        address = socket.gethostbyname(
            socket.gethostname()
        )

        if address:
            return address

    except Exception:
        pass

    return "127.0.0.1"


# =========================================================
# PAIRING INFO
# =========================================================

def get_pairing_info():
    settings = (
        load_remote_settings()
    )

    ip_address = (
        get_local_ip()
    )

    port = settings[
        "port"
    ]

    return {
        "ip":
            ip_address,

        "port":
            port,

        "token":
            settings[
                "pairing_token"
            ],

        "url":
            (
                f"http://"
                f"{ip_address}:"
                f"{port}"
            ),
    }


def print_pairing_info():
    info = (
        get_pairing_info()
    )

    print()
    print(
        "=" * 55
    )
    print(
        "JARVIS REMOTE COMPANION"
    )
    print(
        "=" * 55
    )
    print(
        f'PC IP: {info["ip"]}'
    )
    print(
        f'Port: {info["port"]}'
    )
    print(
        f'Pairing token: {info["token"]}'
    )
    print()
    print(
        "PC pairing page:"
    )
    print(
        f'http://127.0.0.1:{info["port"]}/pair'
    )
    print(
        "=" * 55
    )
    print()