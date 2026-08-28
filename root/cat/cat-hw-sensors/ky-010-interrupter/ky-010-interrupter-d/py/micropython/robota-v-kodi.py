from machine import Pin
import time

pin_s = Pin(2, Pin.IN)   # сигнал KY-010 на цифровому вході GP2

print("Заводь щілину то вільною, то перекритою — дивись на рівень:")
while True:
    level = pin_s.value()
    print("HIGH" if level else "LOW")
    time.sleep_ms(200)
