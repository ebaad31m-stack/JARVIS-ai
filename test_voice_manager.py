from core.voice_manager import (
    start_voice_manager,
    get_command
)

import time


start_voice_manager()


print("Say something...")


while True:

    command = get_command()

    if command:

        print("Detected:", command)

    time.sleep(0.1)