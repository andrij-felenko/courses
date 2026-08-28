# ESP32 (MicroPython) + ADS1115: щуп через зовнішній 16-бітний АЦП по I2C.
from machine import Pin, I2C
import ads1x15                          # драйвер ADS1115 (напр. robert-hh/ads1x15)
import time

power = Pin(25, Pin.OUT)               # щуп живимо з GPIO, як і раніше
i2c = I2C(0, scl=Pin(22), sda=Pin(21)) # SDA/SCL плати
# gain=1 → діапазон входу ±4.096 В під наш сигнал; 0x48 — типова адреса
ads = ads1x15.ADS1115(i2c, 0x48, gain=1)

# калібрування у СИРИХ відліках ADS1115 (16 біт зі своїм PGA) — зняти окремо:
AIR   = 17000                          # сухо
WATER = 9000                           # мокро

def read_avg_ads(ch, n=16):
    total = 0
    for _ in range(n):
        total += ads.read(channel1=ch)  # сирий 16-бітний відлік з каналу
        time.sleep_ms(2)
    return total // n

def to_percent(raw):
    pct = (raw - AIR) * 100 // (WATER - AIR)
    return max(0, min(100, pct))        # затиск у 0…100

power.value(0)
while True:
    power.value(1)
    time.sleep_ms(50)                   # усталення генератора щупа
    raw = read_avg_ads(0)               # AOUT щупа на каналі A0 модуля ADS1115
    power.value(0)

    pct = to_percent(raw)
    print("ADS raw={}  moisture={}%".format(raw, pct))
    time.sleep_ms(2000)
