def aggregate_month(hub_id, rows):            # чистий CPU: перемолоти місяць показань
    # десятки тисяч рядків → перцентилі, ковзні середні, детект аномалій
    total = sum(r["value"] for r in rows)     # (насправді роботи на ~900 мс)
    return {"hub": hub_id, "avg": total / len(rows)}

async def handle_control(reader, writer):
    cmd = (await reader.readline()).split()
    if len(cmd) >= 2 and cmd[0] == b"aggregate":
        hub_id = cmd[1].decode()
        rows = await storage.month(hub_id)             # неблокуюче читання — ок
        summary = aggregate_month(hub_id, rows)        # ОТРУТА: ~900 мс CPU В ЦИКЛІ
        writer.write(json.dumps(summary).encode() + b"\n")
        await writer.drain()
