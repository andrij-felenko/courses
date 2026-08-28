import asyncio

async def stream_to_iter(src, data_event="data", end_event="end"):
    queue: asyncio.Queue = asyncio.Queue()
    _DONE = object()

    def on_data(v): queue.put_nowait(v)
    def on_end():   queue.put_nowait(_DONE)

    src.on(data_event, on_data)
    src.once(end_event, on_end)
    try:
        while True:
            item = await queue.get()      # поспати до наступної події
            if item is _DONE:
                return
            yield item
    finally:
        src.off(data_event, on_data)      # прибрати слухачі й на break, і на кінці
        src.off(end_event, on_end)

# споживання:
async for chunk in stream_to_iter(socket):
    handle(chunk)
    if enough:
        break
