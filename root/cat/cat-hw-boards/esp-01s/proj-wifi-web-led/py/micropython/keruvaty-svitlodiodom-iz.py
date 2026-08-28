import network
import socket
from machine import Pin

SSID = "ВашаМережа"
PASS = "ВашПароль"

led = Pin(2, Pin.OUT)                    # GPIO2, активний НИЗЬКИЙ
led.value(1)                             # старт: погашено

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASS)
while not wlan.isconnected():
    pass

print()
print("Відкрий у браузері: http://" + wlan.ifconfig()[0])  # ось цю адресу — в адресний рядок

# сервер на 80-му порту (HTTP)
server = socket.socket()
server.bind(("", 80))
server.listen(1)                         # почати слухати з'єднання

while True:
    client, addr = server.accept()       # хтось під'єднався (блокуюче очікування)

    # читаємо ПЕРШИЙ рядок запиту — у ньому весь потрібний нам зміст:
    #   "GET /on HTTP/1.1"  →  шлях "/on"
    req = client.readline()

    # за шляхом вирішуємо, що робити зі світлодіодом
    # (пам'ятаємо: 0 = світиться, 1 = гасне)
    if req.find(b"/on") != -1:
        led.value(0)                     # увімкнути
        on = True
    elif req.find(b"/off") != -1:
        led.value(1)                     # вимкнути
        on = False
    else:
        on = (led.value() == 0)          # просто "/" — лишити як є, показати стан

    # проковтуємо решту заголовків запиту, поки браузер їх шле
    while True:
        line = client.readline()
        if not line or line == b"\r\n":
            break

    # ── відповідь: спершу HTTP-заголовок, потім HTML-сторінка ──
    client.send(
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        "Connection: close\r\n"
        "\r\n")                          # порожній рядок = кінець заголовків

    client.send("<!DOCTYPE html><html><head><meta charset='utf-8'>")
    client.send("<meta name='viewport' content='width=device-width'>")
    client.send("<title>ESP-01S</title></head><body>")
    client.send("<h2>Світлодіод зараз: ")
    client.send("<b>увімкнено</b>" if on else "<b>вимкнено</b>")
    client.send("</h2>")
    client.send("<p><a href='/on'>Увімкнути</a> &nbsp; ")
    client.send("<a href='/off'>Вимкнути</a></p>")
    client.send("</body></html>")

    client.close()                       # закрити з'єднання
