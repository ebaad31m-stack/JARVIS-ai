from core.app_launcher import launch_app

from core.system_info import (
    get_cpu,
    get_cpu_usage,
    get_ram,
    get_ram_usage,
    get_windows,
    get_gpu,
    get_gpu_stats,
    get_storage,
    get_system_report
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

    if command == "what is my cpu usage":
        return f"Your CPU usage is {get_cpu_usage()}."


    if command == "how much ram am i using":
        return f"You are using {get_ram_usage()}."


    if command == "what is my gpu status":
        return f"GPU status: {get_gpu_stats()}."


    if command == "system report":
        return get_system_report()



    # =========================
    # UNKNOWN COMMAND
    # =========================

    return None