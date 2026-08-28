telemetry = ServiceClient("telemetry", resolve, http,
    {"pool": 10, "queue": 0,  "wait": 0.0, "timeout": 3.0, "tries": 2, "fails_to_open": 5,  "cooldown": 2.0})
core = ServiceClient("core", resolve, http,
    {"pool": 40, "queue": 40, "wait": 0.2, "timeout": 1.0, "tries": 2, "fails_to_open": 10, "cooldown": 1.0})


# ЧИТАННЯ: телеметрія — прикраса, тож у неї є ЧЕСНИЙ фолбек. Список пристроїв критичний — фолбека нема.
async def main_screen(user_id):
    async def readings_or_empty():
        try:
            return await telemetry.call("/lastReadings", {"userId": user_id})
        except Exception:
            return []                                   # ← фолбек: без виміру
    devices, readings = await asyncio.gather(
        core.call("/listDevices", {"userId": user_id}),  # свій пул; впаде — екран чесно не збереться
        readings_or_empty(),
    )
    by_id = {r["deviceId"]: r for r in readings}
    return [{"device": d, "reading": by_id.get(d["id"])} for d in devices]  # None → плитка «—»


# КОМАНДА: той самий стос — але БЕЗ except-фолбека. Не дотягнулись — помилка нагору.
# Повтор безпечний, бо команду ми зробили ідемпотентною ще на межі з домом.
async def lock_door(device_id):
    return await core.call("/command", {"deviceId": device_id, "op": "lock"})
