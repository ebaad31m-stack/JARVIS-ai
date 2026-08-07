
import os
import tempfile
import time
import threading
import pygame

from elevenlabs.client import ElevenLabs
from config import ELEVENLABS_API_KEY


VOICE_ID = "nPczCjzI2devNBz1zQrb"


client = ElevenLabs(
    api_key=ELEVENLABS_API_KEY
)


pygame.mixer.init(
    frequency=44100,
    size=-16,
    channels=2,
    buffer=512
)


voice_lock = threading.Lock()


def stop_voice():
    """Immediately stop JARVIS's voice."""

    try:
        pygame.mixer.music.stop()

        try:
            pygame.mixer.music.unload()
        except Exception:
            pass

    except Exception as error:

        print("Stop voice error:", error)


def speak(text):
    """Generate and play ElevenLabs speech."""

    output_file = None

    try:

        print("JARVIS:", text)

        # Generate ElevenLabs audio
        audio = client.text_to_speech.convert(
            voice_id=VOICE_ID,
            text=text,
            model_id="eleven_flash_v2_5",
            output_format="mp3_44100_128"
        )

        # Save the generated audio
        with tempfile.NamedTemporaryFile(
            suffix=".mp3",
            delete=False
        ) as file:

            output_file = file.name

            for chunk in audio:
                file.write(chunk)

        # Play the audio
        with voice_lock:

            pygame.mixer.music.load(output_file)

            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():

                time.sleep(0.05)

            try:
                pygame.mixer.music.unload()
            except Exception:
                pass

    except Exception as error:

        print("ElevenLabs voice error:", error)

    finally:

        # Delete temporary MP3
        if output_file:

            try:
                os.remove(output_file)

            except OSError:
                pass

