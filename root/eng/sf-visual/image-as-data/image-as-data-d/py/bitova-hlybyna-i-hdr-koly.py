# Побудувати LUT 10-біт → 8-біт із гамою (раз на старті)
# out = 255 · (in/1023)^(1/γ),  γ≈2.2 — типова гама дисплея
def build_tonemap_lut(gamma):
    lut = [0] * 1024
    for i in range(1024):
        norm = i / 1023.0                   # 0..1
        mapped = norm ** (1.0 / gamma)      # підняти тіні
        v = int(mapped * 255.0 + 0.5)       # у 0..255 з округленням
        lut[i] = 255 if v > 255 else v
    return lut
# у гарячому циклі — лише дешеве звертання до таблиці:
#   shown = lut10to8[raw10 & 0x3FF]
