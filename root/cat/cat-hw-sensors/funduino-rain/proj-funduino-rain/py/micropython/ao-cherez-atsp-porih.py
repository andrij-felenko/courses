from machine import ADC, Pin
import time

ao = ADC(Pin(34))                   # аналоговий вихід давача (ESP32: ADC1)
ao.atten(ADC.ATTN_11DB)             # повна шкала ~3.3 В

while True:
    v = ao.read()                   # 0..4095 на ESP32; менше = мокріше
    print(v)                        # ← дивимося сухе й мокре значення
    time.sleep_ms(300)
