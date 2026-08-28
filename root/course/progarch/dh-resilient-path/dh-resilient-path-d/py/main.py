# Читання телеметрії з BFF — уся політика стійкості в одному стосі.
async def last_readings(ids: list[DeviceId]) -> dict[DeviceId, Reading]:
    async def attempt():
        return await with_timeout(3.0,                    # 3. стеля на цю спробу
            lambda: telemetry.last_readings(ids))
    try:
        async with telemetry_bulkhead.slot():             # 1. слот із пулу телеметрії (≤10) або відмова
            return await telemetry_breaker.call(          # 2. відкритий? → виняток → фолбек
                lambda: with_retry(attempt, tries=2, budget=3.0))  # 4. повтор усередині
    except ResilienceError:
        return {}                                         # 5. будь-яка відмова → фолбек: без виміру
