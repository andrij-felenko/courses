# ESP32 (MicroPython aioble): сервіс оточення + характеристика температури
import aioble, bluetooth

_ENV_SENSE = bluetooth.UUID(0x181A)                     # Environmental Sensing
_TEMP      = bluetooth.UUID(0x2A6E)                     # Temperature

env  = aioble.Service(_ENV_SENSE)
temp = aioble.Characteristic(
    env, _TEMP,
    read=True,                                          # дозволяємо читати
    notify=True)                                        # ...і сповіщати
                                                        # CCCD aioble заводить сам
aioble.register_services(env)

await aioble.advertise(250_000, services=[_ENV_SENSE]) # почали рекламувати себе
