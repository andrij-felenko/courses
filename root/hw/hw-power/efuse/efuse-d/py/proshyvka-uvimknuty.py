from machine import Pin

EFUSE_EN  = 25   # керує ніжкою EN мікросхеми eFuse
EFUSE_FLT = 26   # вхід аварії, активний нуль (open-drain)

en  = Pin(EFUSE_EN,  Pin.OUT)
flt = Pin(EFUSE_FLT, Pin.IN, Pin.PULL_UP)   # підтягнуто до +

def efuse_init():
    en.value(1)                             # відчинити ключ — подати живлення

# True, якщо eFuse ЗАРАЗ сигналить про аварію (FLT == 0)
def efuse_fault():
    return flt.value() == 0
