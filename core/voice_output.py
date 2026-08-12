import os
import subprocess
import tempfile
import threading

import pygame
import requests

from core.paths import resource_file
from core.voice_settings import load_voice_settings


playback_lock = threading.Lock()


def stop_voice():
    try:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()

            try:
                pygame.mixer.music.unload()
            except Exception:
                pass

    except Exception as error:
        print(
            "Voice stop error:",
            error
        )


def speak(text):
    if not text:
        return

    settings = load_voice_settings()

    speak_with_settings(
        text,
        settings
    )


def speak_with_settings(
    text,
    settings
):
    if not text:
        return

    provider = settings.get(
        "provider",
        "piper"
    )

    if provider == "elevenlabs":
        speak_elevenlabs(
            text,
            settings
        )

    else:
        speak_piper(
            text,
            settings
        )


def preview_voice(
    settings
):
    speak_with_settings(
        "Hello, I am JARVIS.",
        settings
    )


# =========================================================
# PIPER
# =========================================================

def speak_piper(
    text,
    settings
):
    piper_exe = resource_file(
        "piper",
        "piper.exe"
    )

    voice_name = settings.get(
        "piper_voice",
        "en_US-lessac-medium.onnx"
    )

    voice_model = resource_file(
        "piper",
        voice_name
    )

    if not os.path.exists(
        piper_exe
    ):
        print(
            "Piper executable missing:",
            piper_exe
        )

        return

    if not os.path.exists(
        voice_model
    ):
        print(
            "Piper voice model missing:",
            voice_model
        )

        return

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav"
    )

    temp_path = temp_file.name

    temp_file.close()

    try:
        subprocess.run(
            [
                piper_exe,
                "--model",
                voice_model,
                "--output_file",
                temp_path
            ],
            input=text,
            text=True,
            check=True,
            creationflags=(
                subprocess.CREATE_NO_WINDOW
                if os.name == "nt"
                else 0
            )
        )

        play_audio(
            temp_path
        )

    except Exception as error:
        print(
            "Piper voice error:",
            error
        )

    finally:
        try:
            if os.path.exists(
                temp_path
            ):
                os.remove(
                    temp_path
                )

        except Exception:
            pass


# =========================================================
# ELEVENLABS
# =========================================================

def speak_elevenlabs(
    text,
    settings
):
    api_key = settings.get(
        "elevenlabs_api_key",
        ""
    ).strip()

    voice_id = settings.get(
        "elevenlabs_voice_id",
        ""
    ).strip()

    model = settings.get(
        "elevenlabs_model",
        "eleven_flash_v2_5"
    ).strip()

    if not api_key:
        print(
            "ElevenLabs API key is missing."
        )

        return

    if not voice_id:
        print(
            "ElevenLabs voice ID is missing."
        )

        return

    url = (
        "https://api.elevenlabs.io/v1/"
        f"text-to-speech/{voice_id}"
    )

    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "text": text,
        "model_id": model
    }

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp3"
    )

    temp_path = temp_file.name

    temp_file.close()

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            params={
                "output_format": "mp3_44100_128"
            },
            timeout=60
        )

        response.raise_for_status()

        with open(
            temp_path,
            "wb"
        ) as file:
            file.write(
                response.content
            )

        play_audio(
            temp_path
        )

    except Exception as error:
        print(
            "ElevenLabs voice error:",
            error
        )

    finally:
        try:
            if os.path.exists(
                temp_path
            ):
                os.remove(
                    temp_path
                )

        except Exception:
            pass


# =========================================================
# AUDIO PLAYBACK
# =========================================================

def play_audio(path):
    with playback_lock:
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()

            pygame.mixer.music.load(
                path
            )

            pygame.mixer.music.play()

            clock = pygame.time.Clock()

            while pygame.mixer.music.get_busy():
                clock.tick(
                    30
                )

            try:
                pygame.mixer.music.unload()
            except Exception:
                pass

        except Exception as error:
            print(
                "Audio playback error:",
                error
            )