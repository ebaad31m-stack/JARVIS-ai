import os
import shutil
import socket
import subprocess

import psutil


# ============================================================
# HELPERS
# ============================================================

def clamp(
    value,
    minimum=0.0,
    maximum=100.0,
):
    try:
        value = float(value)
    except Exception:
        value = 0.0

    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )


def bytes_to_gb(
    value,
):
    try:
        return round(
            float(value)
            / (
                1024 ** 3
            ),
            1,
        )
    except Exception:
        return 0.0


# ============================================================
# CPU
# ============================================================

def get_cpu_usage_percent():
    try:
        return clamp(
            psutil.cpu_percent(
                interval=None
            )
        )
    except Exception:
        return 0.0


# ============================================================
# RAM
# ============================================================

def get_ram_telemetry():
    try:
        memory = psutil.virtual_memory()

        return {
            "used_percent": clamp(
                memory.percent
            ),
            "used_gb": bytes_to_gb(
                memory.used
            ),
            "total_gb": bytes_to_gb(
                memory.total
            ),
        }

    except Exception:
        return {
            "used_percent": 0.0,
            "used_gb": 0.0,
            "total_gb": 0.0,
        }


# ============================================================
# DISK
# ============================================================

def get_disk_telemetry():
    try:
        system_drive = os.environ.get(
            "SystemDrive",
            "C:",
        )

        drive = (
            system_drive
            + "\\"
        )

        disk = shutil.disk_usage(
            drive
        )

        used_percent = (
            0.0
            if disk.total <= 0
            else (
                disk.used
                / disk.total
                * 100.0
            )
        )

        return {
            "used_percent": clamp(
                used_percent
            ),
            "free_gb": bytes_to_gb(
                disk.free
            ),
            "total_gb": bytes_to_gb(
                disk.total
            ),
        }

    except Exception:
        return {
            "used_percent": 0.0,
            "free_gb": 0.0,
            "total_gb": 0.0,
        }


# ============================================================
# GPU
# ============================================================

def _get_gpu_from_nvidia_smi():

    command = [
        "nvidia-smi",
        "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu",
        "--format=csv,noheader,nounits",
    ]

    try:

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=2,
            creationflags=(
                subprocess.CREATE_NO_WINDOW
                if os.name == "nt"
                else 0
            ),
        )

        if result.returncode != 0:
            return None

        line = (
            result.stdout
            .strip()
            .splitlines()
        )

        if not line:
            return None

        parts = [
            item.strip()
            for item in line[0].split(",")
        ]

        if len(parts) < 4:
            return None

        utilization = float(
            parts[0]
        )

        memory_used = float(
            parts[1]
        )

        memory_total = float(
            parts[2]
        )

        temperature = float(
            parts[3]
        )

        return {
            "name": "NVIDIA GPU",
            "usage_percent": clamp(
                utilization
            ),
            "memory_used_mb": memory_used,
            "memory_total_mb": memory_total,
            "temperature": temperature,
            "available": True,
        }

    except Exception:
        return None


def _get_gpu_from_gputil():

    try:

        import GPUtil

        gpus = GPUtil.getGPUs()

        if not gpus:
            return None

        gpu = gpus[0]

        return {
            "name": str(
                getattr(
                    gpu,
                    "name",
                    "NVIDIA GPU",
                )
            ),
            "usage_percent": clamp(
                getattr(
                    gpu,
                    "load",
                    0.0,
                )
                * 100.0
            ),
            "memory_used_mb": float(
                getattr(
                    gpu,
                    "memoryUsed",
                    0.0,
                )
            ),
            "memory_total_mb": float(
                getattr(
                    gpu,
                    "memoryTotal",
                    0.0,
                )
            ),
            "temperature": float(
                getattr(
                    gpu,
                    "temperature",
                    0.0,
                )
            ),
            "available": True,
        }

    except Exception:
        return None


def get_gpu_telemetry():

    result = (
        _get_gpu_from_nvidia_smi()
    )

    if result is not None:
        return result

    result = (
        _get_gpu_from_gputil()
    )

    if result is not None:
        return result

    return {
        "name": "GPU unavailable",
        "usage_percent": 0.0,
        "memory_used_mb": 0.0,
        "memory_total_mb": 0.0,
        "temperature": 0.0,
        "available": False,
    }


# ============================================================
# NETWORK
# ============================================================

def get_network_status():

    try:

        interfaces = (
            psutil.net_if_stats()
        )

        for name, info in interfaces.items():

            name_lower = (
                str(name)
                .lower()
            )

            if any(
                blocked in name_lower
                for blocked in (
                    "loopback",
                    "npcap",
                    "bluetooth",
                    "virtual",
                    "vmware",
                    "hyper-v",
                )
            ):
                continue

            if info.isup:

                return {
                    "online": True,
                    "interface": str(
                        name
                    ),
                }

        return {
            "online": False,
            "interface": "Offline",
        }

    except Exception:
        return {
            "online": False,
            "interface": "Unknown",
        }


# ============================================================
# INTERNET TEST
# ============================================================

def test_internet():

    try:

        socket.create_connection(
            (
                "1.1.1.1",
                53,
            ),
            timeout=0.5,
        ).close()

        return True

    except Exception:

        return False


# ============================================================
# FULL TELEMETRY
# ============================================================

def get_telemetry():

    ram = get_ram_telemetry()
    disk = get_disk_telemetry()
    gpu = get_gpu_telemetry()
    network = get_network_status()

    return {
        "cpu_percent":
            get_cpu_usage_percent(),

        "ram_percent":
            ram["used_percent"],

        "ram_used_gb":
            ram["used_gb"],

        "ram_total_gb":
            ram["total_gb"],

        "disk_percent":
            disk["used_percent"],

        "disk_free_gb":
            disk["free_gb"],

        "disk_total_gb":
            disk["total_gb"],

        "gpu_percent":
            gpu["usage_percent"],

        "gpu_name":
            gpu["name"],

        "gpu_temperature":
            gpu["temperature"],

        "gpu_memory_used":
            gpu["memory_used_mb"],

        "gpu_memory_total":
            gpu["memory_total_mb"],

        "gpu_available":
            gpu["available"],

        "network_online":
            network["online"],

        "network_interface":
            network["interface"],
    }