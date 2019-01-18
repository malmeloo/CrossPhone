import util
from aiohttp import web


class BotsExt:
    def __init__(self, app):
        self.app = app

        routes = [
            web.get('/bots', self.get_all_bots),
            web.get('/bots/{id}', self.get_bot)
        ]
        app.add_routes(routes)

    # GET /bots
    async def get_all_bots(self, request):
        """Returns all registered bots (without token)."""
        bots = list(util.get_bots_cleaned().values())

        return web.json_response(bots)

    # GET /bots/{id}
    async def get_bot(self, request):
        """Returns the bot with the specified ID (or current one)"""
        bot_id = request.match_info['id']

        if bot_id == '@me':
            # return current bot
            token = request.headers.get('Authorization')
            bots = util.get_bots_cleaned()
            bot_info = bots.get(token)
        else:
            bots = self.app['bots']
            bot_info = bots.get(bot_id)

            del bot_info['token']
            bot_info['id'] = bot_id

        return web.json_response(bot_info)


def setup(app):
    ext = BotsExt(app)
    return ext
