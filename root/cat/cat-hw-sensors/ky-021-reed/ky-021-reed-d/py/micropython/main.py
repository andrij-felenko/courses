from machine import Pin
import time

reed = Pin(2, Pin.IN)            # S давача; підтяжка вже на платі KY-021
led  = Pin("LED", Pin.OUT)       # вбудований світлодіод

while True:
    # 0 = геркон замкнений = магніт поряд;  1 = магніту немає
    magnet = reed.value() == 0
    led.value(1 if magnet else 0)
    print("магніт поряд" if magnet else "магніту немає")
    time.sleep_ms(50)
