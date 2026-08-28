# ЦИКЛ ПОДІЙ: одне з'єднання = одна призупинена задача. Стек не зайнятий.
import asyncio

def rss_mb():                                  # VmRSS із /proc — без залежностей
    for ln in open("/proc/self/status"):
        if ln.startswith("VmRSS:"):
            return int(ln.split()[1]) / 1024

async def hold(reader, writer):
    await asyncio.Event().wait()               # спить вічно; смуги не тримає

async def main():
    srv = await asyncio.start_server(hold, "127.0.0.1", 9100)
    async with srv:
        await srv.serve_forever()

asyncio.run(main())
# 10 000 клієнтів під'єдналися → VmRSS ≈ кілька КБ × 10⁴ + база інтерпретатора
