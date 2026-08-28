import asyncio
import threading
import time

def sync_monitoring_agent(loop: asyncio.AbstractEventLoop):
    time.sleep(1.0)
    
    async def async_fetch_status(device_id: int) -> dict:
        await asyncio.sleep(0.05)  # Асинхронний мережевий запит
        return {"device_id": device_id, "status": "ONLINE"}

    # Відправка корутини в цикл подій із фонового потоку
    future = asyncio.run_coroutine_threadsafe(async_fetch_status(101), loop)
    
    # Очікування відповіді у синхронному потоці з таймаутом
    try:
        response = future.result(timeout=3.0)
        print(f"Фоновий потік отримав статус: {response}")
    except TimeoutError:
        print("Таймаут очікування відповіді від циклу подій!")
