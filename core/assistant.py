from core.memory_manager import remember, recall
from core.commands import execute_command
from core.responses import get_response


def start_assistant():

    print("JARVIS is online.")

    while True:

        command = input("You: ")


        if command.lower() == "exit":
            print("JARVIS shutting down.")
            break


        # Memory system
        if command.lower().startswith("my name is"):

            name = command[10:].strip()

            remember("name", name)

            print(f"I'll remember that your name is {name}.")
            continue


        if command.lower() == "what is my name":

            name = recall("name")

            if name:
                print(f"Your name is {name}.")
            else:
                print("I don't know your name yet.")

            continue


        # Command system
        response = execute_command(command)

        if response:
            print(response)
            continue


        # Personality responses
        response = get_response(command)

        if response:
            print(response)
            continue


        print(f"I received: {command}")