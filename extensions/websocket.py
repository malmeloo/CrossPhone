import collections
import aiohttp
from aiohttp import web

import util


class WebSocketExt:
    def __init__(self, app):
        self.app = app
        app.connected_clients = set()

        routes = [
            web.get('/ws/{token}', self.websocket_handler),
            web.get('/clients', self.return_clients)
        ]
        app.add_routes(routes)

    async def websocket_handler(self, request):
        """Handles websocket connections."""
        token = request.match_info.get('token')

        ws = web.WebSocketResponse()
        await ws.prepare(request)

        client = WebSocketClient(ws, token)

        connected_tokens = [c.bot.token for c in self.app.connected_clients]
        if token in connected_tokens:
            await ws.send_json({'error': 'Already connected.'})
            await ws.close()

            return ws

        self.app.connected_clients.add(client)
        print(f'{client.bot.name} connected to websocket.')

        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()
                else:
                    print(msg.data)

        self.app.connected_clients.remove(client)

        print(f'{client.bot.name} disconnected from websocket.')
        return ws

    async def return_clients(self, request):
        connected = [c.bot.name for c in self.app.connected_clients]
        return web.json_response(connected)


class WebSocketClient:
    def __init__(self, ws, token):
        bot = util.get_bots_cleaned().get(token)

        Bot = collections.namedtuple('Bot', 'id name token')

        self.bot = Bot(id=bot.get('id'),
                       name=bot.get('name'),
                       token=token)
        self.ws = ws


def setup(app):
    ext = WebSocketExt(app)
    return ext
