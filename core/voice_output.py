import os
import tempfile
import pygame

from elevenlabs.client import ElevenLabs
from config import ELEVENLABS_API_KEY


VOICE_ID = "nPczCjzI2devNBz1zQrb"


client = ElevenLabs(
    api_key=ELEVENLABS_API_KEY
)


pygame.mixer.init()


def stop_voice():
    pygame.mixer.music.stop()


def speak(text):

    try:

        print("JARVIS:", text)

        audio = client.text_to_speech.convert(
            voice_id=VOICE_ID,
            text=text,
            model_id="eleven_flash_v2_5",
            output_format="mp3_44100_128"
        )


        with tempfile.NamedTemporaryFile(
            suffix=".mp3",
            delete=False
        ) as file:

            for chunk in audio:
                file.write(chunk)

            output_file = file.name


        pygame.mixer.music.load(output_file)
        pygame.mixer.music.play()


        while pygame.mixer.music.get_busy():
            pass


        pygame.mixer.music.unload()
        os.remove(output_file)


    except Exception as error:

        print("ElevenLabs voice error:", error)