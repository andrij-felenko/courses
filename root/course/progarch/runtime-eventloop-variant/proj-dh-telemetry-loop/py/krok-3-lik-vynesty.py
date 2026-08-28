from concurrent.futures import ProcessPoolExecutor

POOL = ProcessPoolExecutor()                  # окремі процеси — оминають GIL

async def handle_control(reader, writer):
    cmd = (await reader.readline()).split()
    if len(cmd) >= 2 and cmd[0] == b"aggregate":
        hub_id = cmd[1].decode()
        rows = await storage.month(hub_id)
        loop = asyncio.get_running_loop()
        summary = await loop.run_in_executor(      # смуга ВІЛЬНА, поки процес рахує
            POOL, aggregate_month, hub_id, rows)
        writer.write(json.dumps(summary).encode() + b"\n")
        await writer.drain()
