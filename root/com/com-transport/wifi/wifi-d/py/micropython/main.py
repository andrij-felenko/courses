import network
import time

SSID = "MyHome"
PASS = "пароль"

wlan = network.WLAN(network.STA_IF)   # режим клієнта (station)
wlan.active(True)
wlan.connect(SSID, PASS)              # скан + автентифікація + асоціація

# чекаємо саме на IP: isconnected() стає True з видачею адреси DHCP
while not wlan.isconnected():
    time.sleep_ms(250)
    print(".", end="")

print("\nIP:", wlan.ifconfig()[0])    # напр. 192.168.1.12 — тепер ми в мережі
