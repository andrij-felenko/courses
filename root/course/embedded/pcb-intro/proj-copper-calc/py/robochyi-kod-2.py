# Переріз мідної стінки via у кв. мілах (наближення тонкої стінки: pi*d*t).
#   drill_mm   — діаметр отвору (свердла), мм
#   plating_um — товщина металізації (мідної стінки), мкм
# Повертає площу в кв. мілах, або -1.0 при некоректних аргументах.
def via_barrel_area_mils2(drill_mm, plating_um):
    if drill_mm <= 0.0 or plating_um <= 0.0:
        return -1.0                        # безглузді розміри — не вгадуємо

    drill_mil   = drill_mm / MM_PER_MIL            # діаметр у мілах
    plating_mil = (plating_um * 1e-3) / MM_PER_MIL  # мкм->мм->мил
    return math.pi * drill_mil * plating_mil  # A ~ периметр * товщина
