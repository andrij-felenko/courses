from machine import Pin

HEATER_ON  = 1
HEATER_OFF = 0

# Викликати НАЙПЕРШИМ у старті — до будь-якої логіки нагріву.
# Значення 0 задаємо тим самим викликом, що вмикає драйвер (value=...),
# тож вивід ніколи не «блимає» одиницею; а доти лінію тримає
# в 0 зовнішня підтяжка-вниз — небезпечного вікна нема.
heater = None

def heater_init_safe():
    global heater
    # value=HEATER_OFF застосовується ще до переходу у вихід → одразу 0
    heater = Pin(PIN_HEATER, Pin.OUT, value=HEATER_OFF)

# Єдина точка ввімкнення — лише коли САМІ переконалися, що можна.
def heater_set(on, sensor_ok):
    heater.value(HEATER_ON if on and sensor_ok else HEATER_OFF)  # сумнів → знеструмлюємо
