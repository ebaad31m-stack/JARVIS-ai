import json
import os
import subprocess
import webbrowser


APP_FILE = "data/apps.json"


def load_apps():

    with open(APP_FILE, "r") as file:
        return json.load(file)


def launch_app(name):

    apps = load_apps()

    if name not in apps:
        return None


    target = apps[name]


    if target.startswith("http"):
        webbrowser.open(target)

    else:
        subprocess.Popen(target)


    return True