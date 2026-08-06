def execute_command(command):

    command = command.lower()

    if command == "hello":
        return "Hello. How can I help?"

    elif command == "who are you":
        return "I am JARVIS, your personal assistant."

    else:
        return None