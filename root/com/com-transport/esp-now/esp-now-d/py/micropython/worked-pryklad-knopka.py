import network, espnow
from machine import Pin
from time import sleep_ms

# MAC приймача — його друкує сам приймач у себе в консолі (wlan.config('mac'))
peer_mac = b'\x24\x6f\x28\x11\x22\x33'
btn = Pin(0, Pin.IN, Pin.PULL_UP)   # кнопка на GPIO0

# радіо вмикаємо, але до мережі НЕ приєднуємось
sta = network.WLAN(network.STA_IF)
sta.active(True)

e = espnow.ESPNow()                 # піднімаємо ESP-NOW — інфраструктура не потрібна
e.active(True)
e.add_peer(peer_mac)                # кому слатимемо — за MAC, додати до списку пар

prev = True
while True:
    pressed = (btn.value() == 0)
    if pressed != prev:             # стан кнопки змінився
        cmd = b'\x01' if pressed else b'\x00'   # один байт: 1 увімкнути, 0 вимкнути
        # send повертає True = радіо приймача квитнуло кадр (MAC-ACK),
        # а НЕ «застосунок обробив»
        ok = e.send(peer_mac, cmd)
        print("ACK" if ok else "нема ACK")
        prev = pressed
    sleep_ms(20)                    # проста антидеренчна пауза
