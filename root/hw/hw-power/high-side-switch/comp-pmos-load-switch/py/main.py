# P-ключ навантаження: NPN-перекладач інвертує всередині себе,
# але для МК логіка пряма — HIGH вмикає стрічку.
from machine import Pin
from time import sleep

load = Pin(5, Pin.OUT)             # → Rb → база NPN
load.value(0)                      # старт вимкнено: NPN off, R1 тримає затвор вгорі

while True:
    load.value(1)                  # увімкнути: NPN тягне затвор вниз, плавний пуск через C
    sleep(2)
    load.value(0)                  # вимкнути: затвор повертається до +12 В
    sleep(2)
