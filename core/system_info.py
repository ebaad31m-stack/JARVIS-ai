import platform
import psutil


def get_cpu():
    return platform.processor()


def get_ram():

    ram = psutil.virtual_memory().total

    ram_gb = round(ram / (1024 ** 3))

    return f"{ram_gb} GB"


def get_windows():

    return platform.system() + " " + platform.release()