# battery_percent.py — напруга елемента → грубий відсоток → рішення вимкнутись.
#   pip install smbus2
from smbus2 import SMBus

INA219 = 0x40        # адреса паливоміра (7-біт)
REG_V  = 0x02        # Bus Voltage

def read_voltage(bus):
    raw = bus.read_word_data(INA219, REG_V)     # word: байти переставлено
    raw = ((raw << 8) | (raw >> 8)) & 0xFFFF    # → big-endian
    return (raw >> 3) * 0.004                    # значущі 13 біт · 4 мВ

# Груба крива розряду одного літієвого елемента (напруга під легким
# навантаженням → відсоток). Не лінійна: літій довго тримає ~3.7 В,
# а наприкінці напруга падає стрімко. Точні числа — під СВІЙ елемент.
CURVE = [
    (4.20, 100), (4.10, 90), (4.00, 80), (3.90, 65),
    (3.80, 50),  (3.70, 40), (3.60, 25), (3.50, 15),
    (3.40, 8),   (3.30, 3),  (3.00, 0),
]

def voltage_to_percent(v):
    if v >= CURVE[0][0]:  return 100
    if v <= CURVE[-1][0]: return 0
    for (v_hi, p_hi), (v_lo, p_lo) in zip(CURVE, CURVE[1:]):
        if v_lo <= v <= v_hi:                    # лінійна інтерполяція в сегменті
            k = (v - v_lo) / (v_hi - v_lo)
            return round(p_lo + k * (p_hi - p_lo))
    return 0

SHUTDOWN_AT = 10   # відсоток, на якому пора гасити систему коректно

with SMBus(1) as bus:
    v = read_voltage(bus)
    pct = voltage_to_percent(v)
    print(f"{v:.3f} В  →  ~{pct}%")
    if pct <= SHUTDOWN_AT:
        print("Низький заряд — коректне вимкнення.")
        # import os, subprocess
        # subprocess.run(["sudo", "shutdown", "-h", "now"])
