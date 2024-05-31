import json

with open("ast.json", "r") as fobj:
    content = json.load(fobj)

with open("ast.json", "w") as fobj:
    json.dump(content, fobj, indent=4)
