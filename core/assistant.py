from core.intent_router import process
from core.voice_output import speak
from core.voice_input import listen
from core.wake_word import wait_for_wake_word
from core.logger import log_info, log_error


def start_assistant():

    try:
        speak("JARVIS is online.")
        log_info("JARVIS started")

        while True:

            # Wait for wake word
            wait_for_wake_word()

            log_info("Wake word detected")

            speak("Yes?")

            # Listen for command
            command = listen()

            if not command:
                log_info("No command detected")
                speak("I didn't catch that.")
                continue


            command = command.strip()

            log_info(f"User command: {command}")


            # Exit command
            if command.lower() == "exit":

                speak("JARVIS shutting down.")
                log_info("JARVIS shutdown")
                break


            # Send command to router
            response = process(command)


            if response:

                speak(response)
                log_info(f"Response: {response}")

            else:

                speak("I don't have a response for that yet.")
                log_info("No response generated")


    except Exception as error:

        log_error(f"Critical error: {error}")
        speak("I encountered an error.")