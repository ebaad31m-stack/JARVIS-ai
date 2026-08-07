import speech_recognition as sr
import threading
import queue


recognizer = sr.Recognizer()

command_queue = queue.Queue()

running = False


def microphone_loop():

    global running

    running = True

    with sr.Microphone() as source:

        print("Microphone manager started.")

        recognizer.adjust_for_ambient_noise(
            source,
            duration=1
        )

        while running:

            try:

                audio = recognizer.listen(
                    source,
                    timeout=1,
                    phrase_time_limit=10
                )


                try:

                    text = recognizer.recognize_google(audio)

                    text = text.lower().strip()

                    print("You:", text)

                    command_queue.put(text)


                except sr.UnknownValueError:
                    pass


            except sr.WaitTimeoutError:
                pass



def start_voice_manager():

    thread = threading.Thread(
        target=microphone_loop,
        daemon=True
    )

    thread.start()



def get_command():

    if not command_queue.empty():

        return command_queue.get()

    return ""



def stop_voice_manager():

    global running

    running = False