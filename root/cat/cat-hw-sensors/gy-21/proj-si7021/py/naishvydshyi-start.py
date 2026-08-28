# CircuitPython: бібліотека adafruit_si7021 (читає й Si7021, і HTU21D)
import time
import board
import busio
import adafruit_si7021

# Підіймаємо шину I2C на своїх ніжках (тут типові для більшості плат):
i2c = busio.I2C(board.SCL, board.SDA)

# Створення об'єкта саме й перевіряє зв'язок: якщо давач не відповідає,
# конструктор кине виняток — ловимо його, бо далі йти немає сенсу.
try:
    sensor = adafruit_si7021.SI7021(i2c)
except (ValueError, OSError):
    raise SystemExit("GY-21 не відповідає. Перевірте живлення й дроти SDA/SCL.")
print("GY-21 на зв'язку.")

while True:
    t = sensor.temperature         # °C
    rh = sensor.relative_humidity  # %
    print(f"T = {t:.2f} °C   RH = {rh:.1f} %")
    time.sleep(2)                  # раз на 2 с — щоб давач не грів сам себе (див. пастки)
