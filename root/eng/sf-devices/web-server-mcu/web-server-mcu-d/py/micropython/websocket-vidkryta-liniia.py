# MicroPython на Microdot: WebSocket ловить кадр і сам штовхає показання.
from microdot.websocket import with_websocket

clients = set()

@app.route("/ws")
@with_websocket
async def ws_handler(req, ws):                   # рукостискання вже позаду
    clients.add(ws)
    try:
        while True:
            frame = await ws.receive()           # кожен кадр від браузера
            handle(frame)                        # ... обробити ...
    finally:
        clients.discard(ws)

# Штовхнути свіже показання ВСІМ підключеним клієнтам (з іншої задачі).
async def ws_push_temperature(t):
    msg = '{"temp":%.1f}' % t
    for ws in clients:                           # пристрій сам ініціює відправку
        await ws.send(msg)
