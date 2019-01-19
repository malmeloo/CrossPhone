import importlib
import json
import logging

from aiohttp import web

import util

PORT = 55555
EXTENSIONS = [
    'extensions.numbers',
    'extensions.bots',
    'extensions.websocket'
]

logging.basicConfig(level=logging.WARNING)

with open('credentials.json') as f:
    dbconfig = json.load(f)


@web.middleware
async def validate_token(request, handler):
    """Validates token and handles JSON responses"""
    token = request.headers.get('Authorization')
    registered_tokens = [b['token'] for b in app['bots'].values()]

    if token not in registered_tokens:
        raise web.HTTPUnauthorized

    resp = await handler(request)
    return resp


@web.middleware
async def error_handler(request, handler):
    """Returns a JSON response on a non-200 response"""
    try:
        resp = await handler(request)
        if str(resp.status).startswith('2'):
            return resp
        message = resp.message
    except web.HTTPException as e:
        if str(e.status).startswith('2'):
            raise
        message = e.reason
    return web.json_response({'error': message})


def add_extension(name):
    extension = importlib.import_module(name)
    extension.setup(app)


app = web.Application(middlewares=[])
app.db = util.DatabaseConnection(host='127.0.0.1',
                                 user=dbconfig['user'],
                                 password=dbconfig['password'],
                                 db=dbconfig['database'])

for ext in EXTENSIONS:
    add_extension(ext)

if __name__ == '__main__':
    web.run_app(app, port=PORT)
