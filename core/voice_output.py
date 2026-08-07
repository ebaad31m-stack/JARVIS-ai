import subprocess
import os
import tempfile
import winsound
import threading


PIPER_PATH = r"C:\JARVIS\piper\piper.exe"
VOICE_MODEL = r"C:\JARVIS\piper\en_US-lessac-medium.onnx"


stop_event = threading.Event()


def stop_voice():

    stop_event.set()

    winsound.PlaySound(
        None,
        winsound.SND_PURGE
    )


def speak(text):

    stop_event.clear()

    try:

        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        ) as audio:

            output_file = audio.name


        command = [
            PIPER_PATH,
            "--model",
            VOICE_MODEL,
            "--output_file",
            output_file,
            "--length_scale",
            "0.9"
        ]


        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            text=True
        )

        process.communicate(text)


        print("JARVIS:", text)


        if not stop_event.is_set():

            winsound.PlaySound(
                output_file,
                winsound.SND_FILENAME
            )


        os.remove(output_file)


    except Exception as error:

        print("Voice error:", error)