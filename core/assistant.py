from core.intent_router import process
from core.voice_output import speak
from core.voice_input import listen
from core.wake_word import wait_for_wake_word


def start_assistant():
    speak("JARVIS is online.")

    while True:
        # Wait until the user says the wake word
        wait_for_wake_word()

        speak("Yes?")

        # Listen for the user's command
        command = listen()

        if not command:
            speak("I didn't catch that.")
            continue

        command = command.strip()

        if command.lower() == "exit":
            speak("JARVIS shutting down.")
            break

        # Let the intent router decide what to do
        response = process(command)

        if response:
            speak(response)