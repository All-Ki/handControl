import json
import os
config = None
def load_config(path="config.json"):
    global config
    if config is not None:
        return config
    
    
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        config = json.load(f)

    return config