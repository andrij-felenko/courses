import asyncio
import threading
import time

def sync_worker_thread(loop: asyncio.AbstractEventLoop):
    time.sleep(1.0)
    
    async def async_database_insert(record_id: int) -> str:
        await asyncio.sleep(0.1)  # Імітація асинхронного запиту
        return f"OK_{record_id}"

    # Безпечний запуск корутини з фонового потоку
    future = asyncio.run_coroutine_threadsafe(async_database_insert(42), loop)
    # Очікування відповіді з таймаутом
    result = future.result(timeout=2.0)
    print(f"Синхронний потік отримав результат: {result}")
