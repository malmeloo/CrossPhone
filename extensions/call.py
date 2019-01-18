from aiohttp import web


class CallExt:
    def __init__(self, app):
        self.app = app

        routes = [
            web.post('/numbers/{number}/call', self.call),
            web.post('/numbers/{number}/decline', self.decline)
        ]
        app.add_routes(routes)

    async def call(self, request):
        """Calls a number."""
        pass

    async def decline(self, request):
        """Declines a call."""


def setup(app):
    ext = CallExt(app)
    return ext
