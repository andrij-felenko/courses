import asyncio
import threading
import time

def hardware_telemetry_thread(loop: asyncio.AbstractEventLoop, async_queue: asyncio.Queue):
    """Синхронний робочий потік: читає дані з USB/COM-порту."""
    while True:
        time.sleep(0.2)  # Імітація блокувального читання з апаратного інтерфейсу
        packet = {"timestamp": time.time(), "voltage": 12.4}
        
        # Потокобезпечна реєстрація додавання елемента в асинхронну чергу
        loop.call_soon_threadsafe(async_queue.put_nowait, packet)

async def telemetry_consumer(async_queue: asyncio.Queue):
    """Асинхронний споживач у головному циклі подій."""
    while True:
        data = await async_queue.get()
        print(f"[Event Loop] Отримано телеметрію: {data}")
        async_queue.task_done()
