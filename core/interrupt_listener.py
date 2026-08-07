import threading

from core.voice_input import listen
from core.voice_output import stop_voice


running = False


def interrupt_loop():

    global running

    running = True

    while running:

        command = listen()

        if not command:
            continue

        command = command.lower().strip()

        if command in {
            "jarvis stop",
            "stop",
            "stop talking",
            "be quiet"
        }:
            stop_voice()


def start_interrupt_listener():

    thread = threading.Thread(
        target=interrupt_loop,
        daemon=True
    )

    thread.start()


def stop_interrupt_listener():

    global running

    running = False