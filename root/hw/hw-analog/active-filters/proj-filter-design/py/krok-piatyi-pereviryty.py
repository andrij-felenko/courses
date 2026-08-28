# Магнітуда однієї ланки ФНЧ на частоті f (в разах, не дБ).
def sk_mag_stage(s: SKStage, f: float) -> float:
    r = f / s.f0
    re = 1.0 - r * r          # (1 − r²)
    im = r / s.Q              # (r/Q)
    return 1.0 / math.sqrt(re * re + im * im)

# Магнітуда всього каскаду на частоті f, у децибелах.
def sk_mag_db(st: list[SKStage], f: float) -> float:
    mag = 1.0
    for s in st:
        mag *= sk_mag_stage(s, f)   # добуток ланок
    return 20.0 * math.log10(mag)   # у дБ

# Прогнати характеристику по частотах (лог-крок) і надрукувати — для звірки форми.
def sk_sweep(st: list[SKStage], f_min: float, f_max: float,
             per_decade: int) -> None:
    mult = 10.0 ** (1.0 / per_decade)
    f = f_min
    while f <= f_max * 1.001:
        print(f"{f:8.0f} Гц   {sk_mag_db(st, f):+7.2f} дБ")
        f *= mult
