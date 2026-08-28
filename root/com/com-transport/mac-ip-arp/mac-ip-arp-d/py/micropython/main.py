import network, socket, time, ubinascii

target = ("192.168.1.42", 5000)      # знаємо IP цілі; MAC — ні, його з'ясує ARP

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("my-ssid", "my-pass")   # підключення: роутер видасть нам IP по DHCP
while not wlan.isconnected():
    time.sleep_ms(200)

# наша IP — її ПРИЗНАЧИЛА мережа (не вшита в чіп):
print("my IP :", wlan.ifconfig()[0])
# наша MAC — ВШИТА в залізо, стала:
print("my MAC:", ubinascii.hexlify(wlan.config("mac"), ":").decode())

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
while True:
    sock.sendto(b"ping", target)     # кажемо лише IP+порт; стек сам: ARP → MAC → кадр
    time.sleep(1)
