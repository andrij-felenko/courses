import asyncio, hashlib

async def handle(reader, writer):
    path = (await reader.readline()).strip()
    if path == b"/health":
        writer.write(b"ok")                 # легкий обробник — миттю
    else:
        h = b"pw"
        for _ in range(3_000_000):          # ОТРУТА: ~200 мс тісного циклу
            h = hashlib.sha256(h).digest()
        writer.write(b"done")
    await writer.drain()
    writer.close()

async def main():
    srv = await asyncio.start_server(handle, "127.0.0.1", 3000)
    async with srv:
        await srv.serve_forever()

asyncio.run(main())
# Поки крутиться хеш, КОЖЕН паралельний /health застигає: цикл подій один.
