import asyncio
import time

async def event_loop_drift_monitor(check_interval: float = 0.05, alert_threshold: float = 0.02):
    """
    Періодично призупиняє виконання на фіксований час і порівнює
    реальний інтервал очікування з розрахунковим.
    """
    while True:
        expected_wake = time.perf_counter() + check_interval
        await asyncio.sleep(check_interval)
        actual_wake = time.perf_counter()
        
        drift = actual_wake - expected_wake
        if drift > alert_threshold:
            print(f"[КРИТИЧНА ЗАТРИМКА] Цикл подій був заблокований на {drift * 1000:.2f} мс!")
