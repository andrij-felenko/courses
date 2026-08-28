RANGE_MAX = 64                   # скільки кодів у ручки (0 .. RANGE_MAX-1)

# Заповнює map[i] результатом пробника за коду затримки i.
# Повертає зібрану карту (довжиною range_max).
def sweep(range_max: int) -> list[bool]:
    pf_map = [False] * range_max
    for code in range(range_max):
        knob_set(code)           # виставили ручку
        settle()                 # пауза на встановлення лінії затримки
        pf_map[code] = probe_once()
    return pf_map
