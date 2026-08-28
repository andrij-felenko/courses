import asyncio
from concurrent.futures import ProcessPoolExecutor

def heavy_prime_search(limit: int) -> int:
    """CPU-bound задача: чисті обчислення на Python."""
    count = 0
    for num in range(2, limit):
        if all(num % i != 0 for i in range(2, int(num**0.5) + 1)):
            count += 1
    return count

async def main():
    loop = asyncio.get_running_loop()
    # Створення пулу дочірніх процесів операційної системи
    with ProcessPoolExecutor() as process_pool:
        # Виклик низькорівневого моста run_in_executor
        result = await loop.run_in_executor(
            process_pool, 
            heavy_prime_search, 
            500_000
        )
        print(f"Знайдено простих чисел: {result}")

if __name__ == "__main__":
    asyncio.run(main())
