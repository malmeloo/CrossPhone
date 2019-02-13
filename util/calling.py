import util

# to use as call ID
CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'


class NumberObject:
    def __init__(self, **kwargs):
        self.number = kwargs.get('number')
        self.desc = kwargs.get('description', '')
        self.bot = self.get_bot_by_id(kwargs.get('id'))
        self.channel_id = kwargs.get('channel_id')
        self.server_id = kwargs.get('server_id')

    def get_bot_by_id(self, bot_id):
        bots = util.get_bots()

        return util.ClientObject(bot_id=bot_id,
                                 name=bots.get('name'),
                                 token=bots.get('token'))


class CallObject:
    def __init__(self, app, caller, recipient):
        self.app = app
        self.caller = caller
        self.recipient = recipient

    @property
    def reachable(self):
        connected = [c.bot.id for c in self.app.connected_clients]

        return self.recipient.bot.id in connected
