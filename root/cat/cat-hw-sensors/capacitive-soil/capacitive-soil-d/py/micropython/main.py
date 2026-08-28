from machine import ADC, Pin
from time import sleep

soil = ADC(Pin(34))            # AOUT давача (ADC-здатний пін)
soil.atten(ADC.ATTN_11DB)      # повний діапазон входу 0…3.3 В
pump = Pin(7, Pin.OUT)         # реле помпи

# калібрувальні межі — зняти для СВОГО щупа (див. нижче)
AIR   = 2500                   # сухо (щуп у повітрі)
WATER = 1350                   # мокро (щуп у воді)

def imap(x, in_lo, in_hi, out_lo, out_hi):
    # аналог Arduino map(): лінійне перевідображення без обмеження
    return (x - in_lo) * (out_hi - out_lo) // (in_hi - in_lo) + out_lo

while True:
    raw = soil.read()                          # 0…4095; сухо ≈ вище
    # перевести в «відсотки вологості»: мокро → 100, сухо → 0
    pct = imap(raw, AIR, WATER, 0, 100)
    pct = max(0, min(100, pct))

    print("raw={}  moisture={}%".format(raw, pct))

    pump.value(1 if pct < 30 else 0)           # сухіше 30% → полити
    sleep(1)
