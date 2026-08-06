from openwakeword.model import Model
import sounddevice as sd
import numpy as np


def wait_for_wake_word():

    model = Model(
        wakeword_models=["hey_jarvis"],
        inference_framework="onnx"
    )

    print("Waiting for wake word...")

    detected = False


    def callback(indata, frames, time, status):

        nonlocal detected

        if detected:
            return

        audio = np.frombuffer(
            indata,
            dtype=np.int16
        )

        prediction = model.predict(audio)

        score = prediction.get(
            "hey_jarvis",
            0
        )


        if score > 0.5:

            print("Wake word detected!")

            detected = True


    with sd.InputStream(
        samplerate=16000,
        channels=1,
        dtype="int16",
        blocksize=1280,
        callback=callback
    ):

        while not detected:
            sd.sleep(100)

    return