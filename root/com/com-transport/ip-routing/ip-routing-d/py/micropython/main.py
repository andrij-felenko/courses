import network

# статична конфігурація: задаємо погляд пристрою на мережу
ip      = "192.168.1.42"     # моя адреса
mask    = "255.255.255.0"    # маска /24 — хто «свої»
gateway = "192.168.1.1"      # шлюз — куди дівати «чужих» (default route)
dns     = "192.168.1.1"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
# ← цими трьома числами описано ВСЮ маршрутизацію вузла (порядок: ip, mask, gateway, dns)
wlan.ifconfig((ip, mask, gateway, dns))
wlan.connect("my-ssid", "my-pass")
while not wlan.isconnected():
    pass

# далі ми лише кажемо КУДИ (IP цілі) — а стек сам вирішить «прямо чи через шлюз»:
#   ціль & mask == ip & mask  →  свій сегмент, шле прямо
#   інакше                     →  кадр на MAC шлюза (gateway), пакет — на кінцеву IP
# напр. socket до будь-якої IP: стек сам накладе маску, вибере рядок,
# знайде MAC потрібного сусіда (цілі або шлюзу) і відправить кадр.
