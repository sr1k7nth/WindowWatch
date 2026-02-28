import json, os

def read():
  if os.path.exists("config.json"):
    with open("config.json", "r+") as f:
      try:
        data = json.load(f)
        return data["threshold_time"]
      except (json.JSONDecodeError, KeyError):
        f.seek(0)
        f.truncate()
        data = {
          "threshold_time": 60
        }
        json.dump(data, f)
        return 60
  else:
    print("config.json doesn't exits!")
    with open("config.json", "x") as f:
      data = {
        "threshold_time": 60
      }
      json.dump(data, f)
    return 60
  

def write(new_threshold):
  if os.path.exists("config.json"):
    with open("config.json", "r+") as f:
      try:
        data = json.load(f)
        f.seek(0)
        f.truncate()
        data["threshold_time"] = new_threshold
        json.dump(data, f)
      except (json.JSONDecodeError, KeyError):
        f.seek(0)
        f.truncate()
        data = {
          "threshold_time": new_threshold
        }
        json.dump(data, f)
  else:
    with open("config.json", "x") as f:
      data = {
        "threshold_time": new_threshold
      }
      json.dump(data, f)