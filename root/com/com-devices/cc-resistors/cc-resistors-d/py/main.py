# MicroPython на ESP32
from machine import ADC, Pin

# Поріги на вході АЦП після дільника 1:1 (мВ)
CC_TH_LOW  = 330   # межа «типова» / «1.5 А»
CC_TH_HIGH = 620   # межа «1.5 А» / «3.0 А»

cc1 = ADC(Pin(34))
cc2 = ADC(Pin(35))
for adc in (cc1, cc2):
    adc.atten(ADC.ATTN_11DB)           # діапазон входу ~0…2.5 В

def read_cc_current_limit():
    """Стеля струму порту в міліамперах."""
    # Беремо більшу з двох CC: активна та, де кабель з'єднав CC джерела.
    v = max(cc1.read_uv() // 1000, cc2.read_uv() // 1000)  # мкВ → мВ

    if v >= CC_TH_HIGH:
        return 3000                     # 3.0 А
    if v >= CC_TH_LOW:
        return 1500                     # 1.5 А
    return 900                          # типовий USB: 0.5–0.9 А

limit_mA = read_cc_current_limit()

# Зарядка тягне 1200 мА — вмикаємо лише якщо порт обіцяє запас.
if limit_mA >= 1500:
    enable_battery_charger()            # безпечно: 1.2 А < 1.5 А
else:
    # Порт дає максимум 0.9 А — заряджати не можна, просяде VBUS.
    run_low_power_only()
