# Напруга на виході ідеальної R-2R лесенки для заданого коду.
# vref — опорна напруга (В); bits — розрядність (напр. 8); code — 0..2^bits-1.
def r2r_voltage(vref, bits, code):
    full = 1 << bits          # 2^bits = число рівнів
    return vref * code / full

# Зворотна задача: який код узяти, щоб дістати бажану напругу (з округленням).
def r2r_code(vref, bits, v_target):
    full = 1 << bits
    raw  = v_target / vref * full            # дробовий «ідеальний» код
    raw  = max(0.0, min(raw, full - 1))      # не вийти за межі шкали
    return int(raw + 0.5)                    # округлення до найближчого коду

# r2r_voltage(3.3, 8, 200) -> ~2.578 В
# r2r_code(3.3, 8, 2.578) -> 200
