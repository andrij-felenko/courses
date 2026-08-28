from machine import Pin
import dht
import time

DHT_PIN = 2                      # ніжка МК, куди прийшла лінія DATA

sensor = dht.DHT11(Pin(DHT_PIN))  # саме DHT11 (не DHT22)

while True:
    time.sleep(2)                # ≥ 1 с між читаннями; беремо 2 с із запасом

    # Давач міг не відповісти — measure() кине виняток. Перевіряймо!
    try:
        sensor.measure()               # запустити однодротовий обмін
        t = sensor.temperature()       # °C
        h = sensor.humidity()          # % RH
    except OSError:
        print("DHT11 не відповів — пропускаю читання")
        continue

    # 0 знаків: DHT11 і так цілі
    print("Temp: {:.0f} C   Hum: {:.0f} %".format(t, h))
