from machine import Pin
import time

PIN_REED = 4                       # S давача KY-021 (GPIO 4)
PIN_LED  = 2                        # вбудований світлодіод (GPIO 2)

reed = Pin(PIN_REED, Pin.IN)       # підтяжка вже на платі — Pin.IN достатньо
led  = Pin(PIN_LED, Pin.OUT)

def magnet_present(pin: Pin) -> bool:
    return pin.value() == 0

while True:
    magnet = magnet_present(reed)
    led.value(1 if magnet else 0)
    print("магніт поряд" if magnet else "магніту немає")
    time.sleep_ms(100)
