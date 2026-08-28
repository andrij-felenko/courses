# autoballoon.py — асинхронний демон автобалонінгу мовою Python
import asyncio
import json
import sys

MIN_RAM_BYTES = 2 * 1024 * 1024 * 1024  # 2 ГБ мінімум
SAFETY_MARGIN_PCT = 0.20                # 20% вільної пам'яті


async def run_autoballoon(socket_path: str):
    reader, writer = await asyncio.open_unix_connection(socket_path)

    # Зчитуємо початкове привітання QMP
    await reader.readline()

    # 1. Узгодження QMP
    writer.write(json.dumps({"execute": "qmp_capabilities"}).encode() + b"\n")
    await writer.drain()
    await reader.readline()

    # 2. Встановлюємо інтервал опитування телеметрії statsq
    poll_cmd = {
        "execute": "qom-set",
        "arguments": {
            "path": "/machine/peripheral/balloon0",
            "property": "guest-stats-polling-interval",
            "value": 2
        }
    }
    writer.write(json.dumps(poll_cmd).encode() + b"\n")
    await writer.drain()
    await reader.readline()

    print(f"[autoballoon] Моніторинг активний для {socket_path}")

    while True:
        await asyncio.sleep(3)

        # Опитування статистики
        get_cmd = {
            "execute": "qom-get",
            "arguments": {
                "path": "/machine/peripheral/balloon0",
                "property": "guest-stats"
            }
        }
        writer.write(json.dumps(get_cmd).encode() + b"\n")
        await writer.drain()

        line = await reader.readline()
        if not line:
            break

        data = json.loads(line.decode())
        stats = data.get("return", {}).get("stats", {})

        total_mem = stats.get("stat-total-memory", 0)
        avail_mem = stats.get("stat-available-memory", 0)

        if total_mem > 0 and avail_mem > 0:
            used_mem = total_mem - avail_mem
            safety = int(total_mem * SAFETY_MARGIN_PCT)
            target_mem = max(MIN_RAM_BYTES, min(total_mem, used_mem + safety))

            print(f"[autoballoon] Total: {total_mem // (1024**2)} MB, "
                  f"Available: {avail_mem // (1024**2)} MB -> "
                  f"Target: {target_mem // (1024**2)} MB")

            balloon_cmd = {
                "execute": "balloon",
                "arguments": {"value": target_mem}
            }
            writer.write(json.dumps(balloon_cmd).encode() + b"\n")
            await writer.drain()
            await reader.readline()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Використання: {sys.argv[0]} <шлях_до_qmp_сокета>")
        sys.exit(1)

    asyncio.run(run_autoballoon(sys.argv[1]))
