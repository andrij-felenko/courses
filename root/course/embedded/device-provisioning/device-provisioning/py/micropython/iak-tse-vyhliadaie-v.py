import network

# Ім'я точки доступу роблять унікальним — зазвичай із хвоста MAC-адреси,
# щоб два однакові пристрої поруч не злилися в одну назву.
def start_provisioning_ap():
    ap = network.WLAN(network.AP_IF)
    mac = ap.config('mac')                  # 6 байтів апаратної адреси
    ssid = 'Thermostat-{:02X}{:02X}'.format(mac[4], mac[5])

    ap.config(
        essid=ssid,
        authmode=network.AUTH_OPEN,         # відкрита — щоб телефон під'єднався без пароля
        channel=1,
        max_clients=4,
    )
    ap.active(True)
    # Тепер пристрій — точка доступу за адресою 192.168.4.1
