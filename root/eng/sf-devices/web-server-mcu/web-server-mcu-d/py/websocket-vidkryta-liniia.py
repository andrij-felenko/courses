# WebSocket на websockets: ловить кадр і сам штовхає показання.
import asyncio, json
import websockets

clients = set()

async def ws_handler(ws):                        # рукостискання вже позаду
    clients.add(ws)
    try:
        async for frame in ws:                   # кожен кадр від браузера
            handle(frame)                        # ... обробити ...
    finally:
        clients.discard(ws)

# Штовхнути свіже показання ВСІМ підключеним клієнтам (з іншої задачі).
async def ws_push_temperature(t):
    msg = json.dumps({"temp": round(t, 1)})
    for ws in clients:                           # сервер сам ініціює відправку
        await ws.send(msg)
