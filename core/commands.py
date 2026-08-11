from core.app_launcher import launch_app, close_app
from core.system_control import shutdown_pc
from core.browser_control import open_website, search_google
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

    command = command.lower().strip()

        # =========================
    # CLOSE APPS
    # =========================

    if command.startswith("close "):
        app_name = command.replace(
            "close ",
            "",
            1
        ).strip()

        result = close_app(app_name)

        if result is True:
            return f"Closing {app_name}."

        if result is False:
            return f"I couldn't close {app_name}."


    if command.startswith("quit "):
        app_name = command.replace(
            "quit ",
            "",
            1
        ).strip()

        result = close_app(app_name)

        if result is True:
            return f"Closing {app_name}."

        if result is False:
            return f"I couldn't close {app_name}."



        # =========================
    # BROWSER CONTROL
    # =========================

    if command.startswith("search google for "):
        query = command.replace(
            "search google for ",
            "",
            1
        ).strip()

        if search_google(query):
            return f"Searching Google for {query}."


    if command.startswith("search for "):
        query = command.replace(
            "search for ",
            "",
            1
        ).strip()

        if search_google(query):
            return f"Searching Google for {query}."


    if command.startswith("open website "):
        website = command.replace(
            "open website ",
            "",
            1
        ).strip()

        if open_website(website):
            return f"Opening {website}."


    if command.startswith("open ") and "." in command:
        website = command.replace(
            "open ",
            "",
            1
        ).strip()

        if open_website(website):
            return f"Opening {website}."


    # =========================
    # APP LAUNCHER
    # =========================

    if command.startswith("open "):
        app_name = command.replace("open ", "", 1).strip()

        result = launch_app(app_name)

        if result is True:
            return f"Opening {app_name}."

        if result is False:
            return f"I couldn't open {app_name}."


    if command.startswith("launch "):
        app_name = command.replace("launch ", "", 1).strip()

        result = launch_app(app_name)

        if result is True:
            return f"Opening {app_name}."

        if result is False:
            return f"I couldn't open {app_name}."


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