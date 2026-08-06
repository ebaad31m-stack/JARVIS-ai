import subprocess
import os
import tempfile
import winsound


PIPER_PATH = r"C:\JARVIS\piper\piper.exe"
VOICE_MODEL = r"C:\JARVIS\piper\en_US-ryan-high.onnx"


def speak(text):

    print("JARVIS:", text)

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
            output_file
        ]

        process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            text=True
        )

        process.communicate(text)

        # Play audio silently
        winsound.PlaySound(
            output_file,
            winsound.SND_FILENAME
        )

        # Delete temporary file
        os.remove(output_file)

    except Exception as error:
        print("Voice error:", error)