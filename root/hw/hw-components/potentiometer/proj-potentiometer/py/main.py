from machine import ADC, Pin
from time import sleep_ms

pot = ADC(Pin(34))             # ADC1-ніжка (Wi-Fi-safe)
pot.atten(ADC.ATTN_11DB)       # повна шкала входу ~3.3 В
pot.width(ADC.WIDTH_12BIT)     # роздільність 0…4095

while True:
    raw = pot.read()                    # 0…4095 — «номер щабля»
    v   = raw * 3.3 / 4095              # назад у вольти: код · опорна / макс. код
    pct = raw * 100 // 4095             # поворот у відсотках
    print("raw={:4d}  v={:.2f}  pos={}%".format(raw, v, pct))
    sleep_ms(100)
