# MicroPython на ESP32 — той самий автомат.
from machine import Pin
import time

# Стани — цілі константи (в MicroPython Enum зазвичай не тягнуть).
IDLE, PURGE, RUNNING, COOLDOWN = range(4)

PURGE_MS    = 2000   # 2 с продувки
COOLDOWN_MS = 3000   # 3 с охолодження

valve = Pin(5, Pin.OUT)
pump  = Pin(6, Pin.OUT)

state = IDLE
t0    = time.ticks_ms()   # мітка входу в поточний стан


def enter(s):
    # Вхід у новий стан: зберегти + перезапустити таймер.
    global state, t0
    state = s
    t0    = time.ticks_ms()


def button_pressed():
    # Детектор натискання — фронт з антибрязкотом (§4.4.5a).
    return False   # заглушка


def fsm_step():
    # Головна функція автомата — зветься щооберту, НЕ блокує.
    now = time.ticks_ms()

    if state == IDLE:
        if button_pressed():
            enter(PURGE)                                   # подія

    elif state == PURGE:
        valve.value(0)                                     # дія стану
        if time.ticks_diff(now, t0) >= PURGE_MS:
            enter(RUNNING)                                 # час

    elif state == RUNNING:
        pump.value(1)
        if button_pressed():
            enter(COOLDOWN)                                # подія

    elif state == COOLDOWN:
        pump.value(0)
        if time.ticks_diff(now, t0) >= COOLDOWN_MS:
            enter(IDLE)                                     # час → коло


while True:
    fsm_step()   # весь автомат — один виклик
