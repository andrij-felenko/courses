from machine import I2C, Pin
from max30102 import MAX30102          # порт SparkFun-логіки на MicroPython
import time

# Спершу задаємо свої ніжки шини (тут — типові для ESP32), 400 кГц.
i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=400000)

# Конструктор ШУКАЄ чип: звертається за 0x57 і читає ідентифікатор.
sensor = MAX30102(i2c=i2c)
if sensor.i2c_address not in i2c.scan() or not sensor.check_part_id():
    print("Чип не знайдено. Перевір живлення, дроти SDA/SCL, підтяжки.")
    while True:                        # далі рухатись немає сенсу
        pass
print("Чип знайдено. Прикладіть палець рівно, без натиску.")

# Налаштовуємо явно свій набір, а не мовчазні замовчування.
sensor.setup_sensor()
sensor.set_led_mode(2)                 # 2 = червоний + інфрачервоний (треба для SpO2)
sensor.set_active_leds_amplitude(0x1F) # ~6.4 мА, спокійний старт
sensor.set_sample_rate(400)            # 400 фіз. відліків/с
sensor.set_pulse_width(411)            # довгий спалах — краще розрізнення
sensor.set_sample_average(4)           # усереднити по 4 — тихіший сигнал
sensor.set_adc_range(4096)             # межа шкали АЦП

while True:
    sensor.check()                     # підкачати FIFO з чипа
    if sensor.available():
        red = sensor.pop_red_from_storage()   # миттєве червоне число
        ir  = sensor.pop_ir_from_storage()    # миттєве інфрачервоне число

        line = "IR={} RED={}".format(ir, red)
        if ir < 50000:
            line += "   — пальця немає?"       # поріг присутності
        print(line)
