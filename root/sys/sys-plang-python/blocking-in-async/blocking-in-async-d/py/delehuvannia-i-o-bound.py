import asyncio
import time

def sync_file_processor(filepath: str) -> int:
    """Синхронна блокувальна функція читання файлу."""
    with open(filepath, "rb") as f:
        data = f.read()
    return len(data)

async def handle_client_request(path: str):
    # Делегування у фоновий системний потік
    file_size = await asyncio.to_thread(sync_file_processor, path)
    print(f"Файл успішно оброблено, розмір: {file_size} байтів")
