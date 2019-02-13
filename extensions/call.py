import asyncio

from aiohttp import web

import util


class CallExt:
    def __init__(self, app):
        self.app = app
        app.pending_calls = set()
        app.ongoing_calls = set()

        routes = [
            web.post('/numbers/{number}/call', self.call),
            web.post('/numbers/{number}/decline', self.decline)
        ]
        app.add_routes(routes)

    async def get_call_object(self, caller_data, recipient_data):
        caller = util.NumberObject(number=caller_data.get('number'),
                                   description=caller_data.get('description'),
                                   id=caller_data.get('botid'),
                                   channel_id=caller_data.get('channelid'),
                                   server_id=caller_data.get('serverid'))
        recipient = util.NumberObject(number=recipient_data.get('number'),
                                      description=recipient_data.get('description'),
                                      id=recipient_data.get('botid'),
                                      channel_id=recipient_data.get('channelid'),
                                      server_id=recipient_data.get('serverid'))

        call_obj = util.CallObject(self.app, caller, recipient)

        return call_obj

    async def broadcast(self, recipient, data):
        """Broadcast a WebSocket message to all recipients specified"""
        ws = next((c.ws for c in self.app.connected_clients
                   if c.bot.id == recipient.bot.id), None)
        if ws is None:
            return ValueError('Couldn\'t find WebSocket client.')

        await ws.send_json(data)

    # POST /numbers/{number}/call?caller={caller}
    async def call(self, request):
        """Calls a number."""
        data = await request.json()

        recipient = request.match_info.get('number')
        caller = data.get('caller')

        caller_data = await self.app.db.get_number(caller)
        recipient_data = await self.app.db.get_number(recipient)

        call = await self.get_call_object(caller_data, recipient_data)

        busy_numbers = self.app.ongoing_calls | self.app.pending_calls
        busy_callers = [c.caller.number for c in busy_numbers]
        busy_recipients = [c.recipient.number for c in busy_numbers]

        if recipient == caller:
            return web.Response(status=400, text='You can\'t call yourself.')

        for pending_call in self.app.pending_calls:
            if pending_call.caller.number == recipient:
                # client is responding to call
                self.app.pending_calls.remove(pending_call)

                await self.broadcast(call.caller, {'type': 'connect',
                                                   'number': recipient})
                await self.broadcast(call.recipient, {'type': 'connect',
                                                      'number': caller})

                self.app.ongoing_calls.add(pending_call)

                return web.json_response(caller_data)

        if caller in busy_callers:
            return web.Response(status=400, text='You are already in a call.')
        elif recipient in busy_recipients:
            return web.Response(status=409, text='The recipient is busy.')
        elif not call.reachable:
            return web.Response(status=409, text='The recipient is unreachable.')

        self.app.pending_calls.add(call)

        # return response
        resp = web.json_response(recipient_data)
        await resp.prepare(request)
        await resp.write_eof()

        await self.broadcast(call.recipient, {'type': 'call',
                                              'number': caller})

        await asyncio.sleep(60)  # 30 secs to answer

        if call in self.app.pending_calls:
            # recipient hasn't answered
            await self.broadcast(call.recipient, {'type': 'cancel',
                                                  'number': caller,
                                                  'reason': 'The call has expired.'})
            await self.broadcast(call.caller, {'type': 'decline',
                                               'number': recipient,
                                               'reason': 'The recipient didn\'t answer in time.'})
            self.app.pending_calls.remove(call)

        return resp

    async def decline(self, request):
        """Declines a call."""
        pass


def setup(app):
    ext = CallExt(app)
    return ext
