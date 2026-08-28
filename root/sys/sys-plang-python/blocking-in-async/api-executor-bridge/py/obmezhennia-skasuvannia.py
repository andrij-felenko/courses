import asyncio
import time

def blocking_disk_operation(filename: str, retry_count: int = 3) -> int:
    time.sleep(0.5)
    return len(filename) * retry_count

async def handle_request():
    # Безпечне винесення виклику без зупинки циклу подій
    result = await asyncio.to_thread(blocking_disk_operation, "report.pdf", retry_count=5)
    print(f"Обчислено розмір: {result}")
