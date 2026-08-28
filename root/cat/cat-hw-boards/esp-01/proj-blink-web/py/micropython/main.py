# MicroPython на ESP-01: сокет видно наскрізь, тож обидві справи в одному циклі.
import network, socket, select, time
from machine import Pin

SSID, PASSWORD = "MyHomeWiFi", "supersecret"
BLINK_MS = 1000

# GPIO2: катод світлодіода тут (спосіб B), логіка ІНВЕРСНА: 0 світить, 1 гасне
led = Pin(2, Pin.OUT, value=1)
led_on = False

wlan = network.WLAN(network.STA_IF)     # режим клієнта, не точки доступу
wlan.active(True)
print("Приєднуюся до", SSID)
wlan.connect(SSID, PASSWORD)
while not wlan.isconnected():           # приєднання йде у фоні — чекаємо й підморгуємо
    led.value(0); time.sleep_ms(100)
    led.value(1); time.sleep_ms(400)
    print(".", end="")
print("\nПриєднано. IP:", wlan.ifconfig()[0])

srv = socket.socket()
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("0.0.0.0", 80))
srv.listen(1)
poller = select.poll()
poller.register(srv, select.POLLIN)
print("Веб-сервер запущено")

t0 = time.ticks_ms()
last = t0
while True:
    # Чекаємо запит щонайбільше 20 мс — цикл лишається чуйним і до годинника
    if poller.poll(20):
        cl, _ = srv.accept()
        cl.recv(512)
        up_sec = time.ticks_diff(time.ticks_ms(), t0) // 1000
        html = ("<!DOCTYPE html><html><head><meta charset='utf-8'><title>ESP-01</title>"
                "</head><body><h2>ESP-01 живий</h2><p>Працює: %d с</p>"
                "<p>Світлодіод: %s</p></body></html>"
                % (up_sec, "увімкнено" if led_on else "вимкнено"))
        cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n"
                "Connection: close\r\n\r\n")
        cl.send(html)
        cl.close()

    now = time.ticks_ms()
    if time.ticks_diff(now, last) >= BLINK_MS:
        last = now
        led_on = not led_on
        led.value(0 if led_on else 1)    # 0 світить (спосіб B)
