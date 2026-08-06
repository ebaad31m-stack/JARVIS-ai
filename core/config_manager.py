import json
import os


class ConfigManager:

    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load_config()


    def load_config(self):

        if not os.path.exists(self.config_file):

            self.save_config({})
            return {}


        try:

            with open(self.config_file, "r") as file:
                return json.load(file)


        except json.JSONDecodeError:

            print("Config file corrupted. Resetting.")

            self.save_config({})
            return {}



    def get(self, key, default=None):

        return self.config.get(key, default)



    def set(self, key, value):

        self.config[key] = value
        self.save_config(self.config)



    def save_config(self, data):

        with open(self.config_file, "w") as file:
            json.dump(data, file, indent=4)