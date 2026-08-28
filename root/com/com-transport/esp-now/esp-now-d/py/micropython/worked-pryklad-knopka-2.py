import network, espnow
from machine import Pin

lamp = Pin(2, Pin.OUT)              # лампа на GPIO2

sta = network.WLAN(network.STA_IF)
sta.active(True)
print(sta.config('mac'))           # ← цей MAC вписуємо в peer_mac передавача

e = espnow.ESPNow()
e.active(True)                      # усе: тепер кадри можна приймати

# у MicroPython немає recv-callback — читаємо кадри циклом (uasyncio-стилю),
# стек сам будить recv(), щойно кадр прилітає
while True:
    host, data = e.recv()          # блокує, доки не прийде кадр
    if data and len(data) >= 1:    # порожній кадр — ігноруємо
        lamp.value(1 if data[0] else 0)   # перший байт керує лампою
