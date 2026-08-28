from machine import Pin, ADC
import network
import time

# ADC1 на S3 — це GPIO1..GPIO10; беремо один із них.
ADC_PIN = 3     # GPIO3 = ADC1_CH2 — придатний під активне радіо

adc = ADC(Pin(ADC_PIN))
# Розширюємо діапазон входу до повних ~3.3 В (найбільше згасання сигналу).
adc.atten(ADC.ATTN_11DB)

# Вмикаємо Wi-Fi, щоб показати: на ADC1 виміри лишаються чистими.
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("SSID", "PASSWORD")   # підстав свою мережу
print("Wi-Fi піднято; читаю ADC1...")

while True:
    raw = adc.read()                # 0..8191 (13 біт на S3!)
    mv = adc.read_uv() // 1000       # мікровольти → мілівольти, з калібруванням

    print("сире = {:4d}   напруга = {} мВ ({:.3f} В)".format(
        raw, mv, mv / 1000.0))
    time.sleep_ms(500)
