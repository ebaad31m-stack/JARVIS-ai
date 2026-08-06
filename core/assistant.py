from core.memory_manager import remember, recall


def start_assistant():

    print("JARVIS is online.")

    while True:
        command = input("You: ")

        if command.lower() == "exit":
            print("JARVIS shutting down.")
            break


        if command.lower().startswith("my name is"):
            name = command[11:].strip()

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


        print(f"I received: {command}")