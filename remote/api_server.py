from __future__ import annotations

import ipaddress
import secrets
import threading

from flask import (
    Flask,
    jsonify,
    request,
)

from waitress import serve

from core.action_manager import (
    get_action_state,
)

from remote.remote_manager import (
    execute_remote_command,
)

from remote.remote_settings import (
    get_pairing_info,
    load_remote_settings,
)


SERVER_VERSION = "1.1"


app = Flask(
    __name__
)


_server_thread = None

_server_lock = (
    threading.Lock()
)


# =========================================================
# NETWORK SAFETY
# =========================================================

def _client_is_local() -> bool:

    address = (
        request.remote_addr
        or ""
    )

    try:

        ip = ipaddress.ip_address(
            address
        )

        return (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
        )

    except ValueError:
        return False


def _reject_non_local():

    if not _client_is_local():

        return (
            jsonify(
                {
                    "ok": False,
                    "error":
                        "JARVIS Remote only accepts "
                        "local network connections.",
                }
            ),
            403,
        )

    return None


# =========================================================
# AUTHENTICATION
# =========================================================

def _authorized() -> bool:

    settings = (
        load_remote_settings()
    )

    expected_token = str(
        settings.get(
            "pairing_token",
            "",
        )
    )

    supplied_token = str(
        request.headers.get(
            "X-JARVIS-Token",
            "",
        )
    )

    if not expected_token:
        return False

    if not supplied_token:
        return False

    return secrets.compare_digest(
        supplied_token,
        expected_token,
    )


def _require_auth():

    local_error = (
        _reject_non_local()
    )

    if local_error is not None:
        return local_error

    if not _authorized():

        return (
            jsonify(
                {
                    "ok": False,
                    "error":
                        "Invalid JARVIS pairing token.",
                }
            ),
            401,
        )

    return None


# =========================================================
# HOME
# =========================================================

@app.route(
    "/",
    methods=["GET"],
)
def home():

    local_error = (
        _reject_non_local()
    )

    if local_error is not None:
        return local_error

    return jsonify(
        {
            "ok": True,
            "name": "JARVIS Remote API",
            "version": SERVER_VERSION,
        }
    )


# =========================================================
# PING
# =========================================================

@app.route(
    "/api/ping",
    methods=["GET"],
)
def ping():

    local_error = (
        _reject_non_local()
    )

    if local_error is not None:
        return local_error

    return jsonify(
        {
            "ok": True,
            "message": "JARVIS is reachable.",
            "version": SERVER_VERSION,
        }
    )


# =========================================================
# PAIRING PAGE
# =========================================================

@app.route(
    "/pair",
    methods=["GET"],
)
def pair():

    address = (
        request.remote_addr
        or ""
    )

    try:

        ip = ipaddress.ip_address(
            address
        )

    except ValueError:

        return (
            "Invalid request.",
            403,
        )

    if not ip.is_loopback:

        return (
            "The pairing page can only "
            "be opened on the JARVIS PC.",
            403,
        )

    info = (
        get_pairing_info()
    )

    pc_ip = (
        info.get(
            "ip",
            ""
        )
    )

    port = (
        info.get(
            "port",
            8765,
        )
    )

    token = (
        info.get(
            "token",
            ""
        )
    )

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>JARVIS Pairing</title>
        <meta charset="utf-8">

        <style>
            body {{
                background: #080c12;
                color: #e8f7ff;
                font-family:
                    Segoe UI,
                    Arial,
                    sans-serif;
                padding: 40px;
            }}

            .card {{
                max-width: 700px;
                margin: auto;
                padding: 30px;
                border-radius: 18px;
                background: #101824;
                border: 1px solid #1d89b8;
            }}

            h1 {{
                color: #5edbff;
            }}

            .value {{
                padding: 12px;
                margin-top: 8px;
                border-radius: 8px;
                background: #071018;
                font-family: Consolas, monospace;
                word-break: break-all;
            }}

            .warning {{
                margin-top: 25px;
                color: #ffcf67;
            }}
        </style>
    </head>

    <body>

        <div class="card">

            <h1>JARVIS Companion Pairing</h1>

            <p>PC IP</p>
            <div class="value">
                {pc_ip}
            </div>

            <p>Port</p>
            <div class="value">
                {port}
            </div>

            <p>Pairing Token</p>
            <div class="value">
                {token}
            </div>

            <p class="warning">
                Keep your pairing token private.
            </p>

        </div>

    </body>
    </html>
    """


# =========================================================
# STATUS
# =========================================================

@app.route(
    "/api/status",
    methods=["GET"],
)
def status():

    auth_error = (
        _require_auth()
    )

    if auth_error is not None:
        return auth_error

    action_state = (
        get_action_state()
    )

    return jsonify(
        {
            "ok": True,
            "message":
                "Connected to JARVIS.",

            "version":
                SERVER_VERSION,

            "suggestions":
                action_state.get(
                    "suggestions",
                    [],
                ),

            "pending_action":
                action_state.get(
                    "pending",
                ),
        }
    )


# =========================================================
# COMMAND
# =========================================================

@app.route(
    "/api/command",
    methods=["POST"],
)
def command():

    auth_error = (
        _require_auth()
    )

    if auth_error is not None:
        return auth_error

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )

    command_text = str(
        data.get(
            "command",
            "",
        )
    ).strip()

    if not command_text:

        return (
            jsonify(
                {
                    "ok": False,
                    "error":
                        "Command is required.",
                }
            ),
            400,
        )

    try:

        response = (
            execute_remote_command(
                command_text
            )
        )

        action_state = (
            get_action_state()
        )

        return jsonify(
            {
                "ok": True,

                "response":
                    response,

                "suggestions":
                    action_state.get(
                        "suggestions",
                        [],
                    ),

                "pending_action":
                    action_state.get(
                        "pending",
                    ),
            }
        )

    except Exception as error:

        return (
            jsonify(
                {
                    "ok": False,
                    "error":
                        str(error),
                }
            ),
            500,
        )


# =========================================================
# SERVER
# =========================================================

def _server_worker(
    host: str,
    port: int,
):

    print(
        f"[Remote] JARVIS API running on "
        f"{host}:{port}"
    )

    serve(
        app,
        host=host,
        port=port,
        threads=4,
    )


def start_remote_server() -> bool:

    global _server_thread

    with _server_lock:

        if (
            _server_thread is not None
            and _server_thread.is_alive()
        ):
            return True

        settings = (
            load_remote_settings()
        )

        enabled = bool(
            settings.get(
                "enabled",
                True,
            )
        )

        if not enabled:

            print(
                "[Remote] Remote server disabled."
            )

            return False

        host = str(
            settings.get(
                "host",
                "0.0.0.0",
            )
        )

        try:

            port = int(
                settings.get(
                    "port",
                    8765,
                )
            )

        except Exception:

            port = 8765

        _server_thread = threading.Thread(
            target=_server_worker,
            args=(
                host,
                port,
            ),
            daemon=True,
            name="JARVIS-Remote-API",
        )

        _server_thread.start()

        return True