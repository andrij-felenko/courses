# MicroPython (ESP32). ADC1, 12 біт; PIN_RAW — вузол подільника напряму,
# PIN_BUF — вихід повторювача → той самий вузол
from machine import ADC, Pin
import time

PIN_RAW = 34   # ADC1 (GPIO34), напряму до МОм-подільника
PIN_BUF = 35   # ADC1 (GPIO35), вихід ОП-буфера

adc_raw = ADC(Pin(PIN_RAW))
adc_buf = ADC(Pin(PIN_BUF))
adc_raw.atten(ADC.ATTN_0DB)   # якщо Vin > 1 В — ADC.ATTN_11DB
adc_buf.atten(ADC.ATTN_0DB)

def avg_mv(adc, n):
    s = 0
    for _ in range(n):
        s += adc.read_uv()       # рідні мікровольти ESP32
    return s // n // 1000        # → мілівольти

while True:
    raw = avg_mv(adc_raw, 16)    # високий опір джерела — занижує
    buf = avg_mv(adc_buf, 16)    # через буфер — істина
    # Очікуваний вивід:
    #   raw=945 mV  buf=1670 mV  dif=+725 mV   (джерело ~1.72 В, 1 МОм подільник)
    #   або raw≈buf (джерело й так низькоомне — буфер зайвий)
    print("raw={} mV  buf={} mV  dif={} mV".format(raw, buf, buf - raw))
    time.sleep_ms(200)
