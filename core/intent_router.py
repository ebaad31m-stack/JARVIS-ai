from core.memory_manager import remember, recall
from core.commands import execute_command
from core.responses import get_response


def process(command):

    command = command.lower()

    # =========================
    # MEMORY
    # =========================

    if command.startswith("my name is"):

        name = command[10:].strip()

        remember("name", name)

        return f"I'll remember that your name is {name}."

    if command == "what is my name":

        name = recall("name")

        if name:
            return f"Your name is {name}."

        return "I don't know your name yet."

    # =========================
    # COMMANDS
    # =========================

    response = execute_command(command)

    if response:
        return response

    # =========================
    # PERSONALITY
    # =========================

    response = get_response(command)

    if response:
        return response

    return "I'm not sure how to help with that yet."