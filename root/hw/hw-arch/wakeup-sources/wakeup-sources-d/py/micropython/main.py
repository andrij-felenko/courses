import machine
import esp32
from machine import Pin

WAKE_GPIO     = 36            # мусить бути RTC-здатною ніжкою!
SLEEP_MINUTES = 15
MS_PER_MIN    = 60000        # мілісекунд у хвилині

# 1. Чому нас підняли?
cause = machine.wake_reason()
if cause == machine.TIMER_WAKE:          # сплив період
    handle_periodic_measurement()
elif cause == machine.EXT0_WAKE:         # натиснули кнопку
    handle_button_press()
else:                                    # перше холодне ввімкнення
    cold_start_init()

# 2. Вмикаємо ОБИДВА сторожі перед сном.
#    ext0 будить рівнем 0 (LOW) на RTC-ніжці.
esp32.wake_on_ext0(pin=Pin(WAKE_GPIO), level=esp32.WAKEUP_ALL_LOW)

# 3. У глибокий сон — таймер задають самим викликом deepsleep(ms);
#    прокинемося від того, що настане раніше.
machine.deepsleep(SLEEP_MINUTES * MS_PER_MIN)
# Рядки нижче не виконуються: deep-sleep перезапускає чип з початку.
