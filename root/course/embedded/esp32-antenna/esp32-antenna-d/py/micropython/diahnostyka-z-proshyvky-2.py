import network, time

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

while True:
    nets = wlan.scan()                  # блокуючий скан усіх каналів
    print("знайдено мереж:", len(nets))

    strong = 0                          # скільки з них гучніші за −80 dBm
    for ssid, bssid, ch, rssi, sec, hidden in nets:
        if rssi > -80:
            strong += 1
        print("  %-24s  %4d dBm  ch%d" % (ssid.decode(), rssi, ch))

    print("з них упевнених (> −80 dBm):", strong, "\n")
    time.sleep(5)
