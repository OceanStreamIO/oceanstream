import json
from pathlib import Path

DEFAULT_CONFIG_PATH = Path(__file__).parent / 'defaults.config.json'


def load_config(user_config_path=None):
    with open(DEFAULT_CONFIG_PATH, 'r') as file:
        config = json.load(file)

    if user_config_path and Path(user_config_path).exists():
        with open(user_config_path, 'r') as file:
            user_config = json.load(file)
        for key in user_config:
            config[key].update(user_config[key])

    return config
