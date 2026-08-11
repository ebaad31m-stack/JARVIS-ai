import subprocess


def shutdown_pc():
    try:
        subprocess.Popen(
            ["shutdown", "/s", "/t", "0"]
        )

        return True

    except Exception as error:
        print("Shutdown error:", error)
        return False