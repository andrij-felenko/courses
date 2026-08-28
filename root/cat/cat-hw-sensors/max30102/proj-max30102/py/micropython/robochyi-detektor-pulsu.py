from machine import I2C, Pin
from max30102 import MAX30102
from heartrate import check_for_beat   # детектор ударів (PBA)
import time

RATE_SIZE = 4                          # по скількох останніх BPM усереднюємо
rates = [0] * RATE_SIZE                # кільцевий буфер значень
rate_spot = 0
last_beat = 0                          # час попереднього удару, мс

beats_per_minute = 0.0
beat_avg = 0

i2c = I2C(0, sda=Pin(21), scl=Pin(22), freq=400000)
sensor = MAX30102(i2c=i2c)
if not sensor.check_part_id():
    print("Чип не знайдено. Перевір живлення/дроти.")
    while True:
        pass
print("Прикладіть палець з рівним, легким натиском.")

sensor.setup_sensor()                       # типові налаштування достатні
sensor.set_pulse_amplitude_red(0x0A)        # тьмяний червоний — індикатор «живе»
# зеленого на MAX30102 немає — нічого й не вмикаємо

while True:
    sensor.check()
    if not sensor.available():
        continue
    ir_value = sensor.pop_ir_from_storage()

    if check_for_beat(ir_value):            # щойно стався удар?
        delta = time.ticks_diff(time.ticks_ms(), last_beat)
        last_beat = time.ticks_ms()

        beats_per_minute = 60000.0 / delta  # миттєвий пульс

        if 20 < beats_per_minute < 255:     # відсіяти дурню
            rates[rate_spot] = int(beats_per_minute)
            rate_spot = (rate_spot + 1) % RATE_SIZE   # рух по кільцю

            beat_avg = sum(rates) // RATE_SIZE        # середнє по буферу

    line = "IR={} BPM={} AvgBPM={}".format(ir_value, beats_per_minute, beat_avg)
    if ir_value < 50000:
        line += "   — пальця немає?"
    print(line)
