from machine import ADC, Pin
import time

ao = ADC(Pin(34))                   # ADC1! GPIO34 безпечний при Wi-Fi
ao.atten(ADC.ATTN_11DB)             # повна шкала ~3.3 В
DRY_ENTER_MV = 2400                 # пороги — тепер у мілівольтах
WET_ENTER_MV = 1500

raining = False

while True:
    mv = ao.read_uv() // 1000        # відкалібровані мілівольти (read_uv → мкВ)

    if not raining and mv < WET_ENTER_MV:
        raining = True
    if raining and mv > DRY_ENTER_MV:
        raining = False

    print("AO =", mv, "мВ", "  → дощ" if raining else "  → сухо")
    time.sleep_ms(200)
