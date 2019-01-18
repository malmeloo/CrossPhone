import random

import util
from aiohttp import web


class NumbersExt:
    def __init__(self, app):
        self.app = app

        routes = [
            web.get('/numbers', self.get_all_numbers),
            web.get('/numbers/{number}', self.get_number),
            web.post('/numbers', self.register)
        ]
        app.add_routes(routes)

    async def generate_number(self):
        existing_numbers = await self.app.db.get_all_numbers(row='number')

        def gen_rand_num():
            num1 = str(random.randint(0, 999)).zfill(3)
            num2 = str(random.randint(0, 999)).zfill(3)

            return f'{num1}-{num2}'

        number = gen_rand_num()
        while number in existing_numbers:
            # avoid dupes
            number = gen_rand_num()

        return number

    # GET /numbers
    async def get_all_numbers(self, request):
        numbers = await self.app.db.get_all_numbers(row='number')

        return web.json_response(numbers)

    # GET /numbers/{number}
    async def get_number(self, request):
        """Fetches info about an existing phone number."""
        number = request.match_info.get('number')
        number_info = await self.app.db.get_number(number)

        if not number_info:
            return web.Response(status=400, text='Unknown number.')

        return web.json_response(number_info)

    # POST /numbers
    async def register(self, request):
        """Creates a new phone number entry"""
        data = await request.json()
        token = request.headers.get('Authorization')

        bots = util.get_bots_cleaned()
        bot_id = bots[token]['id']

        number = await self.generate_number()

        desc = data.get('description')
        c_id = data.get('channelid')
        s_id = data.get('serverid')

        if not all((desc, c_id, s_id)):
            # insufficient arguments
            return web.Response(status=400, text='Missing one or more arguments.')

        await self.app.db.add_number(number, bot_id, desc, c_id, s_id)

        return web.json_response({'number': number})


def setup(app):
    ext = NumbersExt(app)
    return ext
