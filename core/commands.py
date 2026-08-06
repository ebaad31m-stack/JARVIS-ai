from core.app_launcher import launch_app

from core.system_info import (
    get_cpu,
    get_ram,
    get_windows,
    get_gpu,
    get_storage
)


def execute_command(command):

    command = command.lower()


    # =========================
    # APP LAUNCHER
    # =========================

    if command.startswith("open "):

        app_name = command[5:].strip()

        result = launch_app(app_name)

        if result:
            return f"Opening {app_name}."


    # =========================
    # SYSTEM INFORMATION
    # =========================

    if command == "what cpu do i have":
        return f"You have: {get_cpu()}."


    if command == "what ram do i have":
        return f"You have {get_ram()} of RAM."


    if command == "what windows version am i using":
        return f"You are running {get_windows()}."


    if command == "what gpu do i have":
        return f"You have: {get_gpu()}."


    if command == "how much storage do i have":
        return f"You have {get_storage()}."


    # =========================
    # UNKNOWN COMMAND
    # =========================

    return None