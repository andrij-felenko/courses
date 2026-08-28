from machine import ADC, Pin

adc = ADC(Pin(34))          # вхід дільника з NTC-термістором
adc.atten(ADC.ATTN_11DB)    # повний діапазон входу до ~3.3 В

def sensor_read_temperature():
    # Приклад: NTC-термістор через дільник, кілька відліків АЦП і усереднення.
    N = 8
    acc = sum(adc.read_u16() for _ in range(N))   # 16-біт відлік
    raw = acc / N

    # → напруга → опір термістора → температура (спрощено, реальне — таблиця/Стейнгарт).
    v = raw / 65535.0 * 3.3
    r_ntc = R_FIXED * v / (3.3 - v)
    temp = ntc_resistance_to_celsius(r_ntc)       # ваша калібрувальна функція
    return temp
