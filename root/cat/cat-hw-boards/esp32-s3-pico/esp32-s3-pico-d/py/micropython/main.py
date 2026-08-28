import network, time
from machine import Pin
from neopixel import NeoPixel

led = NeoPixel(Pin(21), 1)          # 1 діод на GPIO21
led[0] = (0, 40, 0)                 # тьмяно-зелений
led.write()                         # «плата ожила»

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("SSID", "пароль")
while not wlan.isconnected():
    time.sleep_ms(300)
    print(".", end="")

print("\nПідключено, IP:", wlan.ifconfig()[0])
