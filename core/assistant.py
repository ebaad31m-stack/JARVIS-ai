import time

from core.intent_router import process
from core.voice_output import speak, stop_voice
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


STOP_COMMANDS = {
    "jarvis stop",
    "stop",
    "stop talking",
    "be quiet"
}


IDLE_TIMEOUT = 120


def start_assistant():

    speak("JARVIS is online.")

    while True:

        print("Waiting for wake word...")

        wait_for_wake_word()

        speak("I'm listening.")

        last_activity = time.time()

        while True:

            command = listen()

            if not command:

                if time.time() - last_activity > IDLE_TIMEOUT:
                    speak(
                        "Going back to sleep due to inactivity."
                    )
                    break

                continue


            last_activity = time.time()

            command = command.strip().lower()


            if command in STOP_COMMANDS:
                stop_voice()
                continue


            if command == "exit":
                speak("JARVIS shutting down.")
                return


            if command in SLEEP_COMMANDS:
                speak("Going back to sleep.")
                break


            speak("Let me think.")

            response = process(command)

            if response:
                speak(response)