import pyttsx3


def speak(text):

    print("JARVIS:", text)

    try:
        engine = pyttsx3.init()

        engine.setProperty("rate", 175)
        engine.setProperty("volume", 1.0)

        engine.say(text)

        engine.runAndWait()

        engine.stop()

    except Exception as error:

        print("Voice error:", error)