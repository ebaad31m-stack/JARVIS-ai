import os
import subprocess
import tempfile
import threading

import numpy as np
import pygame
import requests
import soundfile as sf

from core.paths import resource_file
from core.voice_settings import load_voice_settings
from core.personalization import (
    apply_phrase_override,
)

playback_lock = threading.Lock()

kokoro_pipeline = None
kokoro_pipeline_language = None
kokoro_pipeline_repo = None
kokoro_pipeline_lock = threading.Lock()


# =========================================================
# STOP VOICE
# =========================================================

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
            error,
        )


# =========================================================
# SPEAK
# =========================================================

def speak(
    text
):
    text = apply_phrase_override(text)

    if not text:
        return

    settings = load_voice_settings()

    speak_with_settings(
        text,
        settings,
    )


def speak_with_settings(
    text,
    settings,
):
    if not text:
        return

    provider = (
        str(
            settings.get(
                "provider",
                "piper",
            )
        )
        .lower()
        .strip()
    )

    if provider == "kokoro":
        speak_kokoro(
            text,
            settings,
        )

    elif provider == "elevenlabs":
        speak_elevenlabs(
            text,
            settings,
        )

    elif provider == "xtts":
        speak_xtts(
            text,
            settings,
        )

    else:
        speak_piper(
            text,
            settings,
        )


def preview_voice(
    settings
):
    speak_with_settings(
        "Hello, I am Jarvis.",
        settings,
    )


# =========================================================
# TEXT NORMALIZATION
# =========================================================

def normalize_tts_text(
    text
):
    text = str(
        text
    )

    # Kokoro tends to spell JARVIS when all letters are uppercase.
    text = text.replace(
        "JARVIS",
        "Jarvis",
    )

    return text


# =========================================================
# PIPER
# =========================================================

def speak_piper(
    text,
    settings,
):
    piper_exe = resource_file(
        "piper",
        "piper.exe",
    )

    voice_name = settings.get(
        "piper_voice",
        "en_US-lessac-medium.onnx",
    )

    voice_model = resource_file(
        "piper",
        voice_name,
    )

    if not os.path.exists(
        piper_exe
    ):
        print(
            "Piper executable missing:",
            piper_exe,
        )

        return

    if not os.path.exists(
        voice_model
    ):
        print(
            "Piper voice model missing:",
            voice_model,
        )

        return

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav",
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
                temp_path,
            ],
            input=normalize_tts_text(
                text
            ),
            text=True,
            check=True,
            creationflags=(
                subprocess.CREATE_NO_WINDOW
                if os.name == "nt"
                else 0
            ),
        )

        play_audio(
            temp_path
        )

    except Exception as error:
        print(
            "Piper voice error:",
            error,
        )

    finally:
        safe_delete(
            temp_path
        )


# =========================================================
# KOKORO
# =========================================================

def get_kokoro_pipeline(
    settings
):
    global kokoro_pipeline
    global kokoro_pipeline_language
    global kokoro_pipeline_repo

    language = (
        str(
            settings.get(
                "kokoro_language",
                "b",
            )
        )
        .strip()
    )

    repo_id = (
        str(
            settings.get(
                "kokoro_repo_id",
                "hexgrad/Kokoro-82M",
            )
        )
        .strip()
    )

    with kokoro_pipeline_lock:
        if (
            kokoro_pipeline is not None
            and kokoro_pipeline_language == language
            and kokoro_pipeline_repo == repo_id
        ):
            return kokoro_pipeline

        try:
            from kokoro import KPipeline

            print(
                "Loading Kokoro..."
            )

            kokoro_pipeline = KPipeline(
                lang_code=language,
                repo_id=repo_id,
            )

            kokoro_pipeline_language = language
            kokoro_pipeline_repo = repo_id

            print(
                "Kokoro loaded."
            )

            return kokoro_pipeline

        except Exception as error:
            print(
                "Kokoro load error:",
                error,
            )

            kokoro_pipeline = None

            return None


def speak_kokoro(
    text,
    settings,
):
    pipeline = get_kokoro_pipeline(
        settings
    )

    if pipeline is None:
        return

    voice = (
        str(
            settings.get(
                "kokoro_voice",
                "bm_george",
            )
        )
        .strip()
    )

    try:
        speed = float(
            settings.get(
                "kokoro_speed",
                1.05,
            )
        )

    except Exception:
        speed = 1.05

    speed = max(
        0.50,
        min(
            speed,
            2.00,
        ),
    )

    text = normalize_tts_text(
        text
    )

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav",
    )

    temp_path = temp_file.name
    temp_file.close()

    try:
        generator = pipeline(
            text,
            voice=voice,
            speed=speed,
        )

        audio_chunks = []

        for result in generator:
            if hasattr(
                result,
                "audio",
            ):
                audio = result.audio

            else:
                _, _, audio = result

            if audio is not None:
                audio_chunks.append(
                    np.asarray(
                        audio
                    )
                )

        if not audio_chunks:
            print(
                "Kokoro returned no audio."
            )

            return

        combined_audio = np.concatenate(
            audio_chunks
        )

        sf.write(
            temp_path,
            combined_audio,
            24000,
        )

        play_audio(
            temp_path
        )

    except Exception as error:
        print(
            "Kokoro voice error:",
            error,
        )

    finally:
        safe_delete(
            temp_path
        )


# =========================================================
# XTTS
# =========================================================

def speak_xtts(
    text,
    settings,
):
    print(
        "XTTS v2 support has not been installed yet."
    )

    print(
        "Choose Piper, Kokoro, or ElevenLabs for now."
    )


# =========================================================
# ELEVENLABS
# =========================================================

def speak_elevenlabs(
    text,
    settings,
):
    api_key = (
        str(
            settings.get(
                "elevenlabs_api_key",
                "",
            )
        )
        .strip()
    )

    voice_id = (
        str(
            settings.get(
                "elevenlabs_voice_id",
                "",
            )
        )
        .strip()
    )

    model = (
        str(
            settings.get(
                "elevenlabs_model",
                "eleven_flash_v2_5",
            )
        )
        .strip()
    )

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
        "Content-Type": "application/json",
        "Accept": "audio/mpeg",
    }

    payload = {
        "text": normalize_tts_text(
            text
        ),
        "model_id": model,
    }

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".mp3",
    )

    temp_path = temp_file.name
    temp_file.close()

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            params={
                "output_format":
                    "mp3_44100_128",
            },
            timeout=60,
        )

        print(
            "ElevenLabs HTTP status:",
            response.status_code,
        )

        if not response.ok:
            print(
                "ElevenLabs error response:"
            )

            try:
                print(
                    response.json()
                )

            except Exception:
                print(
                    response.text
                )

            return

        if not response.content:
            print(
                "ElevenLabs returned no audio."
            )

            return

        with open(
            temp_path,
            "wb",
        ) as file:
            file.write(
                response.content
            )

        play_audio(
            temp_path
        )

    except requests.exceptions.Timeout:
        print(
            "ElevenLabs request timed out."
        )

    except requests.exceptions.ConnectionError as error:
        print(
            "ElevenLabs connection error:",
            error,
        )

    except requests.exceptions.RequestException as error:
        print(
            "ElevenLabs request error:",
            error,
        )

    except Exception as error:
        print(
            "ElevenLabs voice error:",
            error,
        )

    finally:
        safe_delete(
            temp_path
        )


# =========================================================
# AUDIO PLAYBACK
# =========================================================

def play_audio(
    path
):
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
                error,
            )


# =========================================================
# TEMP FILE CLEANUP
# =========================================================

def safe_delete(
    path
):
    try:
        if os.path.exists(
            path
        ):
            os.remove(
                path
            )

    except Exception as error:
        print(
            "Temporary audio cleanup error:",
            error,
        )