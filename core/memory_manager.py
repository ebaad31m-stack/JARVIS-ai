import json
import os


MEMORY_FILE = "memory/memory.json"


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {
            "user": {},
            "history": []
        }

    with open(MEMORY_FILE, "r") as file:
        return json.load(file)


def save_memory(memory):
    with open(MEMORY_FILE, "w") as file:
        json.dump(memory, file, indent=4)


def remember(key, value):
    memory = load_memory()

    memory["user"][key] = value

    save_memory(memory)


def recall(key):
    memory = load_memory()

    return memory["user"].get(key, None)