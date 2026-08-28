import asyncio, json

storage = ...  # асинхронний клієнт черги/БД: await storage.put(...) — теж по мережі

async def handle_hub(reader, writer):
    hub = writer.get_extra_info("peername")[0]
    async for raw in reader:                 # рядок за рядком; readline під капотом
        line = raw.strip()
        if not line:
            continue
        try:
            reading = json.loads(line)        # дрібний JSON — швидко, лишаємо в циклі
        except ValueError:
            continue                          # биту телеметрію мовчки кидаємо
        reading["hub"] = hub
        await storage.put(reading)            # await → поки сховище пише, смуга вільна
    writer.close()

async def main():
    srv = await asyncio.start_server(handle_hub, "0.0.0.0", 9099)
    async with srv:
        await srv.serve_forever()

asyncio.run(main())
