import os
import importlib


PLUGIN_FOLDER = "plugins"


plugins = {}


def load_plugins():

    if not os.path.exists(PLUGIN_FOLDER):
        os.makedirs(PLUGIN_FOLDER)

    for file in os.listdir(PLUGIN_FOLDER):

        if file.endswith(".py") and file != "__init__.py":

            plugin_name = file[:-3]

            module = importlib.import_module(
                f"{PLUGIN_FOLDER}.{plugin_name}"
            )

            plugins[plugin_name] = module

            print(f"Loaded plugin: {plugin_name}")


def get_plugin(name):

    return plugins.get(name)