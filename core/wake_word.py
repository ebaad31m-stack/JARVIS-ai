import os

import numpy as np
import sounddevice as sd

from openwakeword.model import Model

from core.personalization import (
    get_custom_wake_model_path,
    get_wake_model,
    get_wake_phrase,
)


WAKE_WORD = "hey_jarvis"

DETECTION_THRESHOLD = 0.5


def _get_model_spec():

    model = get_wake_model()

    if model == "custom":

        custom_path = (
            get_custom_wake_model_path()
        )

        if (
            custom_path
            and os.path.isfile(
                custom_path
            )
        ):

            return custom_path

        print(
            "Custom wake model missing."
        )

        print(
            "Falling back to hey_jarvis."
        )

        return "hey_jarvis"

    return model


def wait_for_wake_word():

    model_spec = _get_model_spec()

    wake_phrase = get_wake_phrase()

    print(
        f"Wake phrase: {wake_phrase}"
    )

    print(
        f"Wake model: {model_spec}"
    )

    try:

        model = Model(
            wakeword_models=[
                model_spec
            ],
            inference_framework="onnx"
        )

    except Exception as error:

        print(
            "Wake model load error:",
            error
        )

        print(
            "Falling back to hey_jarvis."
        )

        model = Model(
            wakeword_models=[
                "hey_jarvis"
            ],
            inference_framework="onnx"
        )

    detected = False

    def callback(
        indata,
        frames,
        time_info,
        status
    ):
        nonlocal detected

        if detected:

            return

        if status:

            print(
                "Wake audio status:",
                status
            )

        audio = np.frombuffer(
            indata,
            dtype=np.int16
        )

        try:

            prediction = (
                model.predict(
                    audio
                )
            )

        except Exception as error:

            print(
                "Wake prediction error:",
                error
            )

            return

        if not prediction:

            return

        score = max(
            float(value)
            for value in prediction.values()
        )

        if score >= DETECTION_THRESHOLD:

            print(
                "Wake word detected!"
            )

            print(
                f"Wake score: {score:.3f}"
            )

            detected = True

    with sd.InputStream(
        samplerate=16000,
        channels=1,
        dtype="int16",
        blocksize=1280,
        callback=callback
    ):

        while not detected:

            sd.sleep(
                100
            )