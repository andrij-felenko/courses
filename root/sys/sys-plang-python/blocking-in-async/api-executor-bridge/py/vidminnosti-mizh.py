import asyncio
from concurrent.futures import ProcessPoolExecutor

def heavy_number_crunching(base: int, exponent: int) -> int:
    return pow(base, exponent, 1_000_000_007)

async def compute():
    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor(max_workers=4) as pool:
        # Виклик процесу для обходу обмежень GIL
        val = await loop.run_in_executor(pool, heavy_number_crunching, 1234567, 9876543)
        print(f"Результат розрахунку: {val}")
