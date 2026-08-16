import html
import ipaddress
import secrets
import socket
import threading

from flask import (
    Flask,
    request,
)

from waitress import serve

from remote.remote_manager import (
    execute_remote_command,
)

from remote.remote_settings import (
    get_pairing_info,
    load_remote_settings,
    print_pairing_info,
)


SERVER_VERSION = "1.0"


app = Flask(
    __name__
)


_server_lock = (
    threading.Lock()
)

_server_started = False


# =========================================================
# CLIENT ADDRESS
# =========================================================

def get_client_address():
    address = (
        request.remote_addr
        or ""
    )

    try:
        return ipaddress.ip_address(
            address
        )

    except Exception:
        return None


# =========================================================
# LAN ONLY
# =========================================================

@app.before_request
def restrict_to_local_network():
    address = (
        get_client_address()
    )

    if address is None:
        return {
            "ok": False,
            "error":
                "Invalid client address.",
        }, 403

    allowed = (
        address.is_private
        or address.is_loopback
        or address.is_link_local
    )

    if not allowed:
        return {
            "ok": False,
            "error":
                "JARVIS Remote is available "
                "only on the local network.",
        }, 403

    return None


# =========================================================
# AUTH
# =========================================================

def request_is_authorized():
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

    try:
        return secrets.compare_digest(
            expected_token,
            supplied_token,
        )

    except Exception:
        return False


def unauthorized_response():
    return {
        "ok": False,
        "error":
            "Invalid JARVIS pairing token.",
    }, 401


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    return {
        "ok": True,
        "name": "JARVIS Remote API",
        "version": SERVER_VERSION,
    }


# =========================================================
# PING
# =========================================================

@app.get("/api/ping")
def ping():
    return {
        "ok": True,
        "name": "JARVIS",
        "message":
            "JARVIS Remote is online.",
        "version":
            SERVER_VERSION,
    }


# =========================================================
# PAIRING PAGE
# =========================================================

@app.get("/pair")
def pairing_page():
    address = (
        get_client_address()
    )

    # Pairing code is visible only from
    # the PC itself.
    if (
        address is None
        or not address.is_loopback
    ):
        return (
            "Pairing information can only "
            "be viewed from the JARVIS PC.",
            403,
        )

    info = (
        get_pairing_info()
    )

    safe_ip = html.escape(
        str(
            info[
                "ip"
            ]
        )
    )

    safe_port = html.escape(
        str(
            info[
                "port"
            ]
        )
    )

    safe_token = html.escape(
        str(
            info[
                "token"
            ]
        )
    )

    return f"""
    <!doctype html>

    <html>
        <head>
            <meta charset="utf-8">

            <title>
                JARVIS Companion Pairing
            </title>

            <style>
                body {{
                    background: #080b10;
                    color: #42e8ff;
                    font-family:
                        Segoe UI,
                        Arial,
                        sans-serif;
                    max-width: 700px;
                    margin: 80px auto;
                    padding: 30px;
                }}

                .card {{
                    border:
                        1px solid
                        #42e8ff;

                    border-radius:
                        16px;

                    padding:
                        30px;

                    box-shadow:
                        0 0 30px
                        rgba(
                            66,
                            232,
                            255,
                            0.20
                        );
                }}

                h1 {{
                    margin-top: 0;
                }}

                code {{
                    color: white;
                    font-size: 18px;
                    word-break:
                        break-all;
                }}

                .warning {{
                    margin-top: 25px;
                    color: #bbbbbb;
                }}
            </style>
        </head>

        <body>
            <div class="card">

                <h1>
                    JARVIS COMPANION
                </h1>

                <p>
                    PC IP
                </p>

                <code>
                    {safe_ip}
                </code>

                <p>
                    Port
                </p>

                <code>
                    {safe_port}
                </code>

                <p>
                    Pairing Token
                </p>

                <code>
                    {safe_token}
                </code>

                <p class="warning">
                    Keep this token private.
                    Enter it only in your
                    JARVIS Companion app.
                </p>

            </div>
        </body>
    </html>
    """


# =========================================================
# AUTHENTICATED STATUS
# =========================================================

@app.get("/api/status")
def status():
    if not request_is_authorized():
        return unauthorized_response()

    settings = (
        load_remote_settings()
    )

    info = (
        get_pairing_info()
    )

    return {
        "ok": True,

        "name":
            "JARVIS",

        "message":
            "Connected to JARVIS.",

        "hostname":
            socket.gethostname(),

        "ip":
            info[
                "ip"
            ],

        "port":
            settings[
                "port"
            ],

        "version":
            SERVER_VERSION,
    }


# =========================================================
# COMMAND ENDPOINT
# =========================================================

@app.post("/api/command")
def command():
    if not request_is_authorized():
        return unauthorized_response()

    payload = (
        request.get_json(
            silent=True
        )
        or {}
    )

    if not isinstance(
        payload,
        dict,
    ):
        return {
            "ok": False,
            "error":
                "Invalid JSON request.",
        }, 400

    raw_command = str(
        payload.get(
            "command",
            "",
        )
    ).strip()

    if not raw_command:
        return {
            "ok": False,
            "error":
                "Command is required.",
        }, 400

    try:
        response = (
            execute_remote_command(
                raw_command
            )
        )

        return {
            "ok": True,

            "command":
                raw_command,

            "response":
                str(
                    response
                ),
        }

    except Exception as error:
        print(
            "Remote API command error:",
            repr(
                error
            ),
        )

        return {
            "ok": False,
            "error":
                "JARVIS could not process "
                "the command.",
        }, 500


# =========================================================
# SERVER THREAD
# =========================================================

def _server_worker(
    host,
    port,
):
    global _server_started

    try:
        print_pairing_info()

        print(
            f"JARVIS Remote server "
            f"listening on port {port}."
        )

        serve(
            app,
            host=host,
            port=port,
            threads=4,
        )

    except Exception as error:
        print(
            "JARVIS Remote server error:",
            repr(
                error
            ),
        )

    finally:
        with _server_lock:
            _server_started = False


# =========================================================
# START
# =========================================================

def start_remote_server():
    global _server_started

    settings = (
        load_remote_settings()
    )

    if not settings.get(
        "enabled",
        True,
    ):
        print(
            "JARVIS Remote is disabled."
        )

        return False

    host = str(
        settings.get(
            "host",
            "0.0.0.0",
        )
    )

    port = int(
        settings.get(
            "port",
            8765,
        )
    )

    with _server_lock:
        if _server_started:
            return True

        _server_started = True

    thread = threading.Thread(
        target=_server_worker,
        args=(
            host,
            port,
        ),
        daemon=True,
        name="JARVIS-Remote-API",
    )

    thread.start()

    return True