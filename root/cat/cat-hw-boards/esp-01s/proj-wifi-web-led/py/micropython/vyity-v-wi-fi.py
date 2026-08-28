import network                           # бібліотека Wi-Fi
from machine import Pin
from time import sleep_ms

SSID = "ВашаМережа"                       # ім'я вашої Wi-Fi
PASS = "ВашПароль"                        # пароль WPA/WPA2

led = Pin(2, Pin.OUT)                     # GPIO2, активний НИЗЬКИЙ
led.value(1)                             # погашено

wlan = network.WLAN(network.STA_IF)      # режим клієнта (station), не точки доступу
wlan.active(True)
wlan.connect(SSID, PASS)                  # почати під'єднання

print("Під'єднуюсь до", SSID, end="")

# чекаємо мережу, блимаючи LED, поки статус не стане «під'єднано»
while not wlan.isconnected():
    led.value(0)                         # блимнути (0 = світиться)
    sleep_ms(100)
    led.value(1)
    sleep_ms(100)
    print(".", end="")

led.value(0)                             # у мережі — лишаємо LED засвіченим
print(" готово!")
print("IP-адреса:", wlan.ifconfig()[0])  # ось за цією адресою нас видно в мережі
