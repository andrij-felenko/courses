from machine import Pin
import time

PIN_DOUT = 3             # DOUT  від HX711  → вхід MCU
PIN_SCK  = 2             # PD_SCK від MCU   → вхід HX711

# Зайві такти задають режим на НАСТУПНИЙ відлік:
#   1 → канал A, підсилення 128;  2 → канал B, 32;  3 → канал A, 64
EXTRA_PULSES = 1         # канал A, ×128 — звичні ваги

dout = Pin(PIN_DOUT, Pin.IN)
sck  = Pin(PIN_SCK, Pin.OUT)
sck.value(0)             # низький рівень — мікросхема не спить


def hx711_ready():
    return dout.value() == 0     # DOUT↓ = дані готові


# Зчитати один відлік. Повертає 24-бітне знакове число
# (доповняльний код збережено).
def hx711_read():
    while not hx711_ready():      # чекаємо спаду DOUT
        pass

    value = 0
    for _ in range(24):          # 24 біти, старший перший
        sck.value(1)
        time.sleep_us(1)
        value = (value << 1) | dout.value()
        sck.value(0)
        time.sleep_us(1)

    for _ in range(EXTRA_PULSES):    # вибір каналу/підсилення
        sck.value(1)
        time.sleep_us(1)
        sck.value(0)
        time.sleep_us(1)

    # розширення знаку: біт 23 — знаковий у доповняльному коді
    if value & 0x800000:
        value -= 0x1000000

    return value


hx711_read()             # холостий зчит: відкинути перший брудний відлік

while True:
    raw = hx711_read()   # сирий код, від −8388608 до +8388607
    print(raw)
    time.sleep_ms(100)
