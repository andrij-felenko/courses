import time
import board
import busio
import digitalio
import adafruit_si7021

RH_ON  = 70.0     # увімкнути тривогу на цій вологості
RH_OFF = 65.0     # вимкнути — лише коли впаде до цієї

i2c = busio.I2C(board.SCL, board.SDA)
try:
    sensor = adafruit_si7021.SI7021(i2c)
except (ValueError, OSError):
    raise SystemExit("GY-21 не відповідає. Перевірте дроти.")

led = digitalio.DigitalInOut(board.LED)   # вбудований світлодіод (на деяких платах — board.D13)
led.direction = digitalio.Direction.OUTPUT

alarm = False     # поточний стан тривоги (пам'ять гістерезису)

while True:
    t  = sensor.temperature
    rh = sensor.relative_humidity

    # -- гістерезис: перемикаємо стан лише на перетині відповідної межі --
    if not alarm and rh >= RH_ON:
        alarm = True
        led.value = True
        print("!! ТРИВОГА: вологість вища за безпечну")
    elif alarm and rh <= RH_OFF:
        alarm = False
        led.value = False
        print("-- вологість повернулась у норму")

    tag = "  [тривога]" if alarm else ""
    print(f"T = {t:.1f} °C  RH = {rh:.1f} %{tag}")
    time.sleep(2)     # раз на 2 с — і давач не гріє себе
