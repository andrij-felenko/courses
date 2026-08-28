import asyncio
import logging
import time

# Налаштування логера для виводу повідомлень відладки asyncio
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

async def problematic_coroutine():
    # Симуляція прихованого блокувального виклику
    time.sleep(0.12)

async def main():
    loop = asyncio.get_running_loop()
    # Зниження порогу реакції до 50 мілісекунд для точної діагностики
    loop.slow_callback_duration = 0.05
    
    task = asyncio.create_task(problematic_coroutine())
    await task

if __name__ == "__main__":
    asyncio.run(main(), debug=True)
