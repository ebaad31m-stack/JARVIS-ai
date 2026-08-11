import time
import threading

from core.intent_router import process
from core.voice_output import speak, stop_voice
from core.voice_input import listen, listen_for_stop
from core.wake_word import wait_for_wake_word
from core.ui_state import set_state, request_shutdown
from core.system_control import shutdown_pc


SLEEP_COMMANDS = {
    "go to sleep",
    "sleep",
    "stop listening",
    "goodbye",
    "jarvis go",
    "jarvis sleep"
}

EXIT_COMMANDS = {
    "exit",
    "jarvis exit",
    "shut down jarvis",
    "shutdown jarvis"
}

PC_SHUTDOWN_COMMANDS = {
    "shut down my computer",
    "shutdown my computer",
    "shut down the computer",
    "shutdown the computer",
    "turn off my computer",
    "turn off the computer",
    "shut down my pc",
    "shutdown my pc",
    "turn off my pc"
}

SHUTDOWN_CONFIRM_COMMANDS = {
    "confirm shutdown",
    "confirm",
    "yes shut down",
    "yes shutdown",
    "yes"
}

SHUTDOWN_CANCEL_COMMANDS = {
    "cancel",
    "cancel shutdown",
    "no",
    "never mind",
    "nevermind"
}


IDLE_TIMEOUT = 120

speaking = False
stop_requested = False
shutdown_pending = False


# =========================
# SPEECH INTERRUPTION
# =========================

def interrupt_monitor():
    global speaking
    global stop_requested

    while speaking:
        try:
            if listen_for_stop():
                print("Interrupt detected!")

                stop_requested = True
                stop_voice()
                speaking = False

                set_state("LISTENING")
                break

        except Exception as error:
            print("Interrupt error:", error)
            break


def speak_with_interrupt(text):
    global speaking
    global stop_requested

    stop_requested = False
    speaking = True

    set_state("SPEAKING")

    monitor = threading.Thread(
        target=interrupt_monitor,
        daemon=True
    )

    monitor.start()

    speech_thread = threading.Thread(
        target=speak,
        args=(text,),
        daemon=True
    )

    speech_thread.start()

    while speech_thread.is_alive():
        if stop_requested:
            stop_voice()
            break

        time.sleep(0.05)

    speaking = False

    if stop_requested:
        stop_voice()


# =========================
# THINKING INTERRUPTION
# =========================

def think_with_interrupt(command):
    global stop_requested

    stop_requested = False

    result = {
        "response": None,
        "finished": False
    }

    def ai_worker():
        try:
            result["response"] = process(command)

        except Exception as error:
            print("AI processing error:", error)
            result["response"] = (
                "I encountered an error while processing that request."
            )

        finally:
            result["finished"] = True

    set_state("THINKING")

    ai_thread = threading.Thread(
        target=ai_worker,
        daemon=True
    )

    ai_thread.start()

    while not result["finished"]:

        try:
            if listen_for_stop():
                print("Thinking interrupted!")

                stop_requested = True

                set_state("LISTENING")

                return None

        except Exception as error:
            print("Thinking interrupt error:", error)

        time.sleep(0.05)

    return result["response"]


# =========================
# MAIN ASSISTANT
# =========================

def start_assistant():
    global stop_requested
    global shutdown_pending

    set_state("SPEAKING")
    speak("JARVIS is online.")

    while True:
        set_state("IDLE")

        print("Waiting for wake word...")
        wait_for_wake_word()

        set_state("SPEAKING")
        speak("I'm listening.")

        set_state("LISTENING")

        last_activity = time.time()

        while True:
            command = listen()

            if not command:

                if time.time() - last_activity > IDLE_TIMEOUT:
                    set_state("SPEAKING")
                    speak("Going back to sleep.")

                    set_state("IDLE")
                    break

                continue

            last_activity = time.time()

            command = command.lower().strip()

            # =========================
            # PC SHUTDOWN CONFIRMATION
            # =========================

            if shutdown_pending:

                if command in SHUTDOWN_CONFIRM_COMMANDS:
                    shutdown_pending = False

                    set_state("SPEAKING")
                    speak("Shutting down, sir.")

                    shutdown_pc()
                    return

                if command in SHUTDOWN_CANCEL_COMMANDS:
                    shutdown_pending = False

                    set_state("SPEAKING")
                    speak("Shutdown cancelled.")

                    set_state("LISTENING")
                    continue

                set_state("SPEAKING")

                speak(
                    "Please say confirm shutdown, "
                    "or cancel shutdown."
                )

                set_state("LISTENING")
                continue

            # =========================
            # EXIT JARVIS
            # =========================

            if command in EXIT_COMMANDS:
                set_state("SPEAKING")

                speak("JARVIS shutting down.")

                set_state("IDLE")

                request_shutdown()
                return

            # =========================
            # SHUTDOWN PC
            # =========================

            if command in PC_SHUTDOWN_COMMANDS:
                shutdown_pending = True

                set_state("SPEAKING")

                speak(
                    "Are you sure, sir? "
                    "Say confirm shutdown."
                )

                set_state("LISTENING")
                continue

            # =========================
            # SLEEP
            # =========================

            if command in SLEEP_COMMANDS:
                set_state("SPEAKING")

                speak("Going back to sleep.")

                set_state("IDLE")
                break

            # =========================
            # NORMAL REQUEST
            # =========================

            speak_with_interrupt(
                "One moment, sir."
            )

            if stop_requested:
                stop_requested = False
                set_state("LISTENING")
                continue

            response = think_with_interrupt(
                command
            )

            # User said "Jarvis stop"
            # while JARVIS was thinking
            if stop_requested:
                stop_requested = False

                set_state("LISTENING")
                continue

            if response:
                speak_with_interrupt(
                    response
                )

            stop_requested = False

            set_state("LISTENING")