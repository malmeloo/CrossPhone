import json

import util


class ClientObject:
    def __init__(self, bot_id, name, token):
        self.id = bot_id
        self.name = name
        self.token = token


class WebSocketClient:
    def __init__(self, ws, token):
        bot = util.get_bots_cleaned().get(token)

        self.bot = util.ClientObject(bot_id=int(bot.get('id')),
                                     name=bot.get('name'),
                                     token=token)
        self.ws = ws


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
