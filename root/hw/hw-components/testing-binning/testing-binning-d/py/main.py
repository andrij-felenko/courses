# Сорти за спаданням: назва + мінімальна гарантована частота, МГц.
BINS = [
    ("топ-сорт",   3600),   # найдорожчий
    ("середній",   3200),
    ("базовий",    2800),
    ("молодший",   2400),
]

# Запас: відсоток на старіння/нагрів + абсолютна добавка на просідання живлення.
GUARD_PERCENT = 7    # 7% на деградацію за роки + температуру
GUARD_FIXED   = 50   # ще 50 МГц «жорсткого» запасу на просідання Vdd

def guaranteed_mhz(fmax_mhz):
    """Гарантована частота = виміряна fmax мінус guard-band."""
    margin = fmax_mhz * GUARD_PERCENT // 100 + GUARD_FIXED
    return fmax_mhz - margin if fmax_mhz > margin else 0

def classify(fmax_mhz):
    """Повертає індекс найвищого сорту, чию планку кристал ще тримає (−1 = брак)."""
    guaranteed = guaranteed_mhz(fmax_mhz)
    for i, (_name, min_mhz) in enumerate(BINS):   # від найдорожчого вниз
        if guaranteed >= min_mhz:
            return i
    return -1                                      # навіть молодший сорт не тягне
