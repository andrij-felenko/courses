import asyncio, time

# ✅ Бюджет на монотонному годиннику — time.monotonic() тільки вгору
# (той самий баг, що в Go, тут дало б time.time() замість time.monotonic()).
class Budget:
    def __init__(self, total):
        self.start, self.total = time.monotonic(), total

    def remaining(self):
        return self.total - (time.monotonic() - self.start)

    def expired(self):
        return self.remaining() <= 0

# Ланцюг під ОДНИМ бюджетом: asyncio.timeout несе дедлайн крізь усі await,
# а міряє його loop.time() — теж монотонний годинник.
async def fetch_reading(addr):
    async with asyncio.timeout(30):        # Python 3.11+; один дедлайн на весь блок
        conn = await connect(addr)         # кожен await бачить свій залишок бюджету
        try:
            raw = await read_frame(conn)   # залишок після connect
            return await parse(raw)        # те, що лишилось
        finally:
            conn.close()
