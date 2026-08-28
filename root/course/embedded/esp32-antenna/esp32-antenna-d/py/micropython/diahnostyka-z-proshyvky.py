import network, time

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("my-ssid", "my-pass")
while not wlan.isconnected():
    time.sleep_ms(200)
print("Підключено, RSSI =", wlan.status("rssi"), "dBm")

while True:
    # антенний «стетоскоп»: 10 замірів RSSI з інтервалом,
    # щоб побачити середнє й розкид — рука/метал одразу видно
    total = 0
    n = 10
    for _ in range(n):
        total += wlan.status("rssi")
        time.sleep_ms(100)
    print("середній RSSI за", n, "замірів:", total // n, "dBm")
    time.sleep(1)
