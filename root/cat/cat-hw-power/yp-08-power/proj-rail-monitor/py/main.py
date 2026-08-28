# MicroPython (ESP32) — рейка 5 В.
# read_uv() повертає МІКРОВОЛЬТИ, уже з заводським калібруванням —
# найпростіший чесний шлях, не треба знати опору вручну.
# 11 dB послаблення: лінійно приблизно до 2.45 В, тож ділимо сильніше:
# R1=15к, R2=10к → k=0.4 → 5.2 В рейки = 2.08 В у вузлі.
from machine import ADC, Pin
import time

R1, R2 = 15000, 10000
DIV = (R1 + R2) / R2          # = 2.5, обернений коефіцієнт
BROWNOUT = 4.6                # поріг тривоги, В

adc = ADC(Pin(34))
adc.atten(ADC.ATTN_11DB)      # діапазон ~0..3.3 В

def read_rail_volts():
    acc = 0
    for _ in range(8):        # усереднення від шуму
        acc += adc.read_uv()  # мікровольти у вузлі, калібровані
    v_node = acc / 8 / 1_000_000   # → вольти на піні
    return v_node * DIV             # → напруга рейки

while True:
    v = read_rail_volts()
    if v < BROWNOUT:
        print("BROWNOUT! рейка = {:.2f} В".format(v))
        # реакція: запалити LED, скинути навантаження…
    else:
        print("рейка OK: {:.2f} В".format(v))
    time.sleep_ms(200)
