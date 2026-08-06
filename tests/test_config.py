from core.config_manager import ConfigManager


def test_config_load():

    config = ConfigManager()

    assert config.get("assistant_name") == "JARVIS"


if __name__ == "__main__":
    test_config_load()
    print("Config test passed!")