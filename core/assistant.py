import time
import threading

from core.intent_router import process
from core.voice_output import speak, stop_voice
from core.voice_input import listen, listen_for_stop
from core.wake_word import wait_for_wake_word


SLEEP_COMMANDS = {
    "go to sleep",
    "sleep",
    "stop listening",
    "goodbye",
    "jarvis go",
    "jarvis sleep"
}


IDLE_TIMEOUT = 120


speaking = False


def interrupt_monitor():

    global speaking

    while speaking:

        if listen_for_stop():

            print("Interrupt detected!")

            stop_voice()

            speaking = False

            break



def speak_with_interrupt(text):

    global speaking

    speaking = True


    monitor = threading.Thread(
        target=interrupt_monitor,
        daemon=True
    )

    monitor.start()


    speak(text)


    speaking = False



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
                        "Going back to sleep."
                    )

                    break

                continue


            last_activity = time.time()

            command = command.lower().strip()


            if command == "exit":

                speak(
                    "JARVIS shutting down."
                )

                return


            if command in SLEEP_COMMANDS:

                speak(
                    "Going back to sleep."
                )

                break


            speak_with_interrupt(
                "Let me think."
            )


            response = process(command)


            if response:

                speak_with_interrupt(response)