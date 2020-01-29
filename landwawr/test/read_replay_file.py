import json

path = "../logs/replay/s01081822_1531_0_0.json"

with open(path, 'r') as f:
    state = json.load(f)

print("done")