import subprocess
import os
import tempfile
import winsound


PIPER_PATH = r"C:\JARVIS\piper\piper.exe"

VOICE_MODEL = r"C:\JARVIS\piper\en_US-lessac-medium.onnx"

def speak(text):

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

        winsound.PlaySound(
            output_file,
            winsound.SND_FILENAME
        )


        os.remove(output_file)


    except Exception as error:
        print("Voice error:", error)