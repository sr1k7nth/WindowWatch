import json
from shared.paths import CONFIG_PATH


def read():
    if not CONFIG_PATH.exists():
        default_data = {"threshold_time": 60}
        CONFIG_PATH.write_text(json.dumps(default_data))
        return 60

    try:
        with open(CONFIG_PATH, "r") as f:
            data = json.load(f)
            return data.get("threshold_time", 60)
    except (json.JSONDecodeError, KeyError):
        default_data = {"threshold_time": 60}
        CONFIG_PATH.write_text(json.dumps(default_data))
        return 60


def write(new_threshold):
    data = {"threshold_time": new_threshold}
    CONFIG_PATH.write_text(json.dumps(data))