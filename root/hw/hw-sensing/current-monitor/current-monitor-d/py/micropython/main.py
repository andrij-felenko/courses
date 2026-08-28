# Монітор струму на ESP32: шунт 5 мОм + підсилювач G=50 + 12-біт АЦП
from machine import ADC, Pin
import time

R_SHUNT = 0.005     # Ом
GAIN    = 50.0      # коефіцієнт підсилювача струму
VREF    = 3.3       # опорна напруга АЦП, В
ADC_MAX = 4095      # 12 біт
i_zero  = 0.0       # калібрований нуль (привид від offset), А
charge_mAh = 0.0    # накопичений заряд

adc = ADC(Pin(34))          # вхід підсилювача → АЦП
adc.atten(ADC.ATTN_11DB)    # діапазон входу до ~3.3 В
adc.width(ADC.WIDTH_12BIT)  # 12 біт → код 0…4095

# Перевести «сирий» код АЦП у струм через шунт (закон Ома, назад через тракт)
def read_current():
    raw   = adc.read()
    v_adc = raw / ADC_MAX * VREF        # напруга на вході АЦП, В
    v_sh  = v_adc / GAIN                # спад на самому шунті, В
    return v_sh / R_SHUNT - i_zero      # I = V/R, мінус нуль

# Калібрування нуля: викликати, коли точно відомо, що струму немає
def calibrate_zero():
    global i_zero
    acc = 0.0
    for _ in range(64):
        acc += read_current() + i_zero
        time.sleep_ms(2)
    i_zero = acc / 64.0                 # усереднений привид від offset

# Інтегрувати заряд: Q += I·Δt  (coulomb counter)
def accumulate_charge(dt_s):
    global charge_mAh
    charge_mAh += read_current() * dt_s / 3.6   # А·с → мА·год: ділимо на 3.6
