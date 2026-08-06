import os
import subprocess
import webbrowser


def execute_command(command):

    command = command.lower()


    # Open calculator
    if command == "open calculator":
        subprocess.Popen("calc.exe")
        return "Opening calculator."


    # Open notepad
    elif command == "open notepad":
        subprocess.Popen("notepad.exe")
        return "Opening notepad."


    # Open Chrome/Google
    elif command in ["open google", "open chrome", "open browser"]:
        webbrowser.open("https://www.google.com")
        return "Opening Google."


    # Unknown command
    return None