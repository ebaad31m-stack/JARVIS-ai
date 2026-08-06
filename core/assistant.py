from core.voice_input import listen
from core.memory_manager import remember, recall
from core.commands import execute_command
from core.responses import get_response
from core.voice_output import speak


def start_assistant():

    speak("JARVIS is online.")

    while True:

        command = listen()
        if not command:
                continue

        if command.lower() == "exit":
            speak("JARVIS shutting down.")
            break


        # =========================
        # MEMORY SYSTEM
        # =========================

        if command.lower().startswith("my name is"):

            name = command[10:].strip()

            remember("name", name)

            speak(f"I'll remember that your name is {name}.")
            continue


        if command.lower() == "what is my name":

            name = recall("name")

            if name:
                speak(f"Your name is {name}.")
            else:
                speak("I don't know your name yet.")

            continue


        # =========================
        # COMMAND SYSTEM
        # =========================

        response = execute_command(command)

        if response:
            speak(response)
            continue


        # =========================
        # PERSONALITY SYSTEM
        # =========================

        response = get_response(command)

        if response:
            speak(response)
            continue


        # =========================
        # UNKNOWN COMMAND
        # =========================

        speak(f"I received: {command}")