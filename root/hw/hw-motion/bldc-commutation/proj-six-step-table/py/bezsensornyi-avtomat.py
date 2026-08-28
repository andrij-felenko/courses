# Безсенсорний автомат: сектор ЖИВЕ у стані й крокує по одному.
g_sector = 0            # поточний рядок 0..5
g_last_sector_us = 0    # тривалість минулого сектора
_prev_zc_us = 0         # час попереднього переходу через нуль

# Викликається з таймера рівно на МЕЖІ сектора (через 30° після нуля).
def commutation_tick(forward):
    global g_sector
    g_sector = (g_sector + 1) % 6 if forward else (g_sector + 5) % 6  # +5 ≡ −1 (mod 6)
    apply_inverter(STEP_FWD[g_sector if forward else (5 - g_sector)])

# Викликається компаратором, коли ЕРС вільної фази перетнула нуль.
def on_zero_crossing(now_us):
    global g_last_sector_us, _prev_zc_us
    g_last_sector_us = now_us - _prev_zc_us   # час між двома нулями = сектор
    _prev_zc_us = now_us
    # чекати 30° = пів сектора, тоді commutation_tick():
    schedule_after(g_last_sector_us // 2, commutation_tick)
