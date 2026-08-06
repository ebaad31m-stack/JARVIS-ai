from core.app_launcher import launch_app


def execute_command(command):

    command = command.lower()


    if command.startswith("open "):

        app_name = command[5:].strip()

        result = launch_app(app_name)

        if result:
            return f"Opening {app_name}."


    return None