from openwakeword.model import Model

import numpy as np
import sounddevice as sd


WAKE_WORD = "hey_jarvis"
DETECTION_THRESHOLD = 0.5


def wait_for_wake_word():
    model = Model(
        wakeword_models=[
            WAKE_WORD
        ],
        inference_framework="onnx"
    )

    print(
        "Waiting for wake word..."
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

        prediction = model.predict(
            audio
        )

        score = prediction.get(
            WAKE_WORD,
            0
        )

        if score > DETECTION_THRESHOLD:
            print(
                "Wake word detected!"
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