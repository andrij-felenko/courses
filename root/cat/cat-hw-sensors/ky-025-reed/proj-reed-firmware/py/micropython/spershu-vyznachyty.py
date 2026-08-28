from machine import Pin
import time

reed = Pin(4, Pin.IN)          # D0 давача на GPIO4; підтяжка Rp вже є на платі KY-025

print("Підносьте й прибирайте магніт, стежте за рівнем D0:")

while True:
    level = reed.value()
    print("D0 = HIGH (високий)" if level == 1 else "D0 = LOW (низький)")
    time.sleep_ms(300)
