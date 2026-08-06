import platform
import psutil
import subprocess


def get_cpu():
    return platform.processor()


def get_cpu_usage():

    usage = psutil.cpu_percent(interval=1)

    return f"{usage}%"


def get_ram():

    ram = psutil.virtual_memory().total

    ram_gb = round(ram / (1024 ** 3))

    return f"{ram_gb} GB"


def get_ram_usage():

    memory = psutil.virtual_memory()

    used = round(memory.used / (1024 ** 3), 1)

    total = round(memory.total / (1024 ** 3), 1)

    percent = memory.percent

    return f"{used}GB / {total}GB ({percent}%)"


def get_windows():

    return platform.system() + " " + platform.release()


def get_gpu():

    try:

        result = subprocess.check_output(
            "nvidia-smi --query-gpu=name --format=csv,noheader",
            shell=True
        )

        return result.decode().strip()

    except:

        return "GPU detection failed."


def get_gpu_stats():

    try:

        result = subprocess.check_output(
            "nvidia-smi --query-gpu=utilization.gpu,temperature.gpu --format=csv,noheader",
            shell=True
        )

        return result.decode().strip()

    except:

        return "GPU stats unavailable."


def get_storage():

    storage = psutil.disk_usage("C:\\")

    free = round(storage.free / (1024 ** 3))

    total = round(storage.total / (1024 ** 3))

    return f"{free}GB free out of {total}GB"