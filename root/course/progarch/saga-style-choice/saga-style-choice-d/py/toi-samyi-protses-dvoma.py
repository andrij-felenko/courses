# ХОРЕОГРАФІЯ: процесу як цілого нема ніде — він розсіяний по обробниках.
@on("DeviceReserveRequested")
async def _(e):
    await registry.reserve(e.device_id, e.home_id)
    emit("DeviceReserved", e)             # хто підхопить — реєстр не знає й знати не хоче

@on("DeviceReserved")
async def _(e):
    try:
        await hub.push_config(e.home_id, e.device_id); emit("DeviceConfigured", e)
    except Exception:
        emit("DeviceConfigFailed", e)     # запускаємо ланцюг компенсацій назад

@on("DeviceConfigured")
async def _(e):
    await billing.start_meter(e.home_id, e.device_id)   # останній крок — тиша означає «готово»

@on("DeviceConfigFailed")
async def _(e):
    await registry.unreserve(e.device_id)  # компенсація теж їде окремою подією
