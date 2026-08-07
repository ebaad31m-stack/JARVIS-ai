from core.intent_router import process
from core.voice_output import speak
from core.voice_input import listen
from core.wake_word import wait_for_wake_word


SLEEP_COMMANDS = {
    "go to sleep",
    "sleep",
    "stop listening",
    "goodbye",
    "jarvis go",
    "jarvis sleep"
}


def start_assistant():

    speak("JARVIS is online.")

    while True:

        print("Waiting for wake word...")

        wait_for_wake_word()

        speak("I'm listening.")

        while True:

            command = listen()

            if not command:
                continue

            command = command.strip().lower()

            if command == "exit":
                speak("JARVIS shutting down.")
                return

            if command in SLEEP_COMMANDS:
                speak("Going back to sleep.")
                break

            response = process(command)

            if response:
                speak(response)