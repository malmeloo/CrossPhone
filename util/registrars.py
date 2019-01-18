import json


def get_bots():
    with open('registered_bots.json') as f:
        bots = json.load(f)

    return bots


def get_bots_cleaned():
    """Returns a dict of bots in a token-friendly way"""
    bots = get_bots()

    cleaned = {data['token']: {"id": id, "name": data['name']}
               for (id, data) in bots.items()}

    return cleaned
