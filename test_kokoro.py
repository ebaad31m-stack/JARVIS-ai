import soundfile as sf

from kokoro import KPipeline


pipeline = KPipeline(
    lang_code="b"
)

text = (
    "Good evening. Jarvis systems are online "
    "and ready for your command."
)

generator = pipeline(
    text,
    voice="bm_george",
    speed=0.92
)

for index, (_, _, audio) in enumerate(generator):
    output_file = f"kokoro_test_{index}.wav"

    sf.write(
        output_file,
        audio,
        24000
    )

    print(
        "Created:",
        output_file
    )