# MicroPython на ESP32: той самий метод двох точок.
# ADC.read() дає 12-бітний код 0..4095; поправку тримаємо в esp32.NVS.
import sys, time
from machine import ADC, Pin
from esp32 import NVS

CAL_PIN = 34
adc = ADC(Pin(CAL_PIN))
adc.atten(ADC.ATTN_11DB)      # фіксуємо atten ДО читання (як analogSetPinAttenuation)
adc.width(ADC.WIDTH_12BIT)

cal = {"raw_lo": 0, "raw_hi": 0, "v_lo": 0.0, "v_hi": 0.0}

# Зняти n відліків і повернути середнє (середнє гасить шум)
def read_avg(n=64):
    return sum(adc.read() for _ in range(n)) // n

# Інтерактивна сесія калібрування через REPL/UART
def run_calibration():
    print("=== Калібрування АЦП ===")
    input("Подайте V_lo (напр. 0.50 В), натисніть Enter: ")
    cal["raw_lo"] = read_avg()
    cal["v_lo"] = float(input("raw_lo = %d. Введіть точне V_lo (В): " % cal["raw_lo"]))

    input("\nПодайте V_hi (напр. 2.50 В), натисніть Enter: ")
    cal["raw_hi"] = read_avg()
    cal["v_hi"] = float(input("raw_hi = %d. Введіть точне V_hi (В): " % cal["raw_hi"]))

    save_calib(cal)
    print("\nКалібрування збережено в NVS.")

# Ініціалізація замість setup(): читаємо поправку, рахуємо slope один раз
if not load_calib(cal):
    print("[WARN] Калібрування відсутнє. Запустіть run_calibration().")
    # cal лишається нулями — apply_calib поверне fallback
else:
    slope = (cal["v_hi"] - cal["v_lo"]) / (cal["raw_hi"] - cal["raw_lo"])
    print("[CAL] slope=%.6f V/код, offset_V=%.4f В"
          % (slope, cal["v_lo"] - slope * cal["raw_lo"]))

# Головний цикл замість loop(): застосування поправки — один рядок
while True:
    raw = adc.read()
    print("%.4f" % apply_calib(cal, raw))
    time.sleep_ms(200)
