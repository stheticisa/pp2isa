import json

def load_settings():
    with open("settings.json","r") as f:
        return json.load(f)

def save_settings(data):
    with open("settings.json","w") as f:
        json.dump(data,f)
