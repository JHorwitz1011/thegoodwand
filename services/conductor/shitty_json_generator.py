import json

a = {
    "action": 'start',
    "cmd": "python3 /home/tgw/spells/first_spell.py"
}

b = {
    "action": 'start',
    "cmd": "python3 /home/tgw/spells/second_spell.py"
}

print(json.dumps(a))

print(json.dumps(b))