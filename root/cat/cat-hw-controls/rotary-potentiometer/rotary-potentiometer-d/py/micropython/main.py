from machine import ADC, Pin
import time

pot = ADC(Pin(26))               # повзунок потенціометра на GP26 (ADC0)

while True:
    raw = pot.read_u16() >> 6    # 16-бітне читання → 0..1023, як у 10-бітного АЦП
    pct = raw * 100 // 1023      # те саме у відсотках 0..100
    print(raw, " ->  ", pct, "%")
    time.sleep_ms(100)
