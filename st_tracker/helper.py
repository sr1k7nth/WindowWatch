import json, os

def read():
  if os.path.exists("config.json"):
    with open("config.json", "r") as f:
      data = json.load(f)
      return data["threshold_time"]
  else:
    print("config.json doesn't exits!")
    return 60
  

def write(new_threshold):
  if os.path.exists("config.json"):
    with open("config.json", "r") as f:
      data = json.load(f)
    with open("config.json", "w") as f:
      data["threshold_time"] = new_threshold
      json.dump(data, f)