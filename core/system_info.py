import platform
import psutil
import subprocess


def get_cpu():
    return platform.processor()


def get_ram():

    ram = psutil.virtual_memory().total

    ram_gb = round(ram / (1024 ** 3))

    return f"{ram_gb} GB"


def get_windows():

    return platform.system() + " " + platform.release()


def get_gpu():

    try:
        result = subprocess.check_output(
            "nvidia-smi --query-gpu=name --format=csv,noheader",
            shell=True
        )

        gpu = result.decode().strip()

        if gpu:
            return gpu

        return "No NVIDIA GPU detected."

    except:
        return "GPU detection failed."


def get_storage():

    storage = psutil.disk_usage("C:\\")

    free = round(storage.free / (1024 ** 3))

    total = round(storage.total / (1024 ** 3))

    return f"{free}GB free out of {total}GB"