# Внесок одного біта k у вихід ідеальної R-2R лесенки (режим напруги).
# k = 0 — молодший біт, k = bits-1 — старший. Вага = Vref / 2^(bits - k).
def r2r_bit_weight(vref, bits, k):
    shift = bits - k                 # N - k
    return vref / (1 << shift)

# Вихід через суму ваг увімкнених бітів — пряме втілення суперпозиції.
# Має збігтися з компактною формулою vref*code/2^bits.
def r2r_voltage_by_bits(vref, bits, code):
    return sum(r2r_bit_weight(vref, bits, k)
               for k in range(bits) if code & (1 << k))   # біт k увімкнений?

# Та сама величина одним множенням — те, що довели на кроках 7-8.
def r2r_voltage(vref, bits, code):
    return vref * code / (1 << bits)

# r2r_voltage_by_bits(3.3, 8, 200) -> ~2.578 В  (1.650 + 0.825 + 0.103)
# r2r_voltage       (3.3, 8, 200) -> ~2.578 В
