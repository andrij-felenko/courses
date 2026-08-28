# Вимір струму BLDC: 3 шунти low-side, центрований ШІМ, відлік у центрі періоду.
# АЦП запускається таймером ШІМ; тут — обробник «перетворення завершено».
R_SHUNT = 0.005    # Ом, шунт під пік струму
GAIN    = 20.0     # коефіцієнт підсилювача струму
VREF    = 3.3      # опорна напруга АЦП, В
ADC_FS  = 4096.0   # повна шкала 12-біт АЦП

# Калібровані «нулі» (код АЦП при I=0): двонапрямлений вимір, нуль ≈ середина шкали.
zero_a = 2048
zero_c = 2048

# миттєві струми фаз, А
ia = ib = ic = 0.0


def adc_to_current(raw, zero):
    """Код АЦП фази → струм у амперах (з урахуванням зсунутого нуля)."""
    v_out = (raw - zero) * (VREF / ADC_FS)   # напруга від нуля, В
    v_sh  = v_out / GAIN                      # спад на шунті, В
    return v_sh / R_SHUNT                     # I = V/R (зі знаком)


def adc_conv_cplt_handler(raw_a, raw_c):
    global ia, ib, ic
    ia = adc_to_current(raw_a, zero_a)   # фаза A з її шунта
    ic = adc_to_current(raw_c, zero_c)   # фаза C з її шунта
    ib = -(ia + ic)                      # фаза B — з правила суми нуль
    # далі: ia, ib, ic → у контур керування моментом (напр. Кларк/Парк для FOC)


# Калібрування нулів: викликати при гарантовано знеструмленому моторі.
_acc_a = _acc_c = _n = 0


def calibrate_zero(raw_a, raw_c):
    global zero_a, zero_c, _acc_a, _acc_c, _n
    _acc_a += raw_a
    _acc_c += raw_c
    _n += 1
    if _n == 256:
        zero_a = _acc_a // 256
        zero_c = _acc_c // 256
        _n = _acc_a = _acc_c = 0
