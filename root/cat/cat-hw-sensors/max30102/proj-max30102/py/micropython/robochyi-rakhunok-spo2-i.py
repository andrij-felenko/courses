from machine import I2C, Pin
from max30102 import MAX30102
from spo2 import spo2_and_heart_rate   # пакетний алгоритм по вікну
import time

BUFFER_LENGTH = 100                    # розмір вікна (≈1 с при 100 відл./с)
# На MicroPython 18-бітні відліки просто лежать у списках цілих —
# без ручного вибору ширини типу, як на 8-бітних AVR.
ir_buffer  = []
red_buffer = []

i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=400000)
sensor = MAX30102(i2c=i2c)
if not sensor.check_part_id():
    print("Чип не знайдено.")
    while True:
        pass

# Явний набір під SpO2: два світлодіоди, 100 відл./с назовні (400/4)
sensor.setup_sensor()
sensor.set_active_leds_amplitude(0x1F)
sensor.set_sample_average(4)
sensor.set_led_mode(2)
sensor.set_sample_rate(400)
sensor.set_pulse_width(411)
sensor.set_adc_range(4096)
print("Прикладіть палець нерухомо.")


def next_sample():
    """Дочекатись однієї пари з FIFO й повернути (red, ir)."""
    while not sensor.available():      # чекаємо новий відлік…
        sensor.check()                 # …підкачуючи FIFO з чипа
    return sensor.pop_red_from_storage(), sensor.pop_ir_from_storage()


# 1. НАБРАТИ перше вікно: 100 пар відліків
for _ in range(BUFFER_LENGTH):
    red, ir = next_sample()
    red_buffer.append(red)
    ir_buffer.append(ir)

# 2. ПОРАХУВАТИ по повному вікну. Функція ПОВЕРТАЄ кортеж —
#    жодних адрес, як у C: значення просто приходять назад.
spo2, valid_spo2, heart_rate, valid_hr = spo2_and_heart_rate(
    ir_buffer, BUFFER_LENGTH, red_buffer)

# 3. Далі — ковзне вікно: викидаємо 25 найстаріших, добираємо 25 свіжих,
#    перераховуємо. Оновлення ~4 рази/с без пауз між вимірами.
while True:
    ir_buffer  = ir_buffer[25:]        # зсунути хвіст уперед
    red_buffer = red_buffer[25:]
    for _ in range(25):                # добрати 25 нових у кінець
        red, ir = next_sample()
        red_buffer.append(red)
        ir_buffer.append(ir)

    spo2, valid_spo2, heart_rate, valid_hr = spo2_and_heart_rate(
        ir_buffer, BUFFER_LENGTH, red_buffer)

    # Показуємо лише те, чому алгоритм довіряє
    hr_text   = "{}".format(heart_rate) if valid_hr else "--"
    spo2_text = "{} %".format(spo2) if valid_spo2 else "-- %"
    print("HR={} bpm, SpO2={}".format(hr_text, spo2_text))
