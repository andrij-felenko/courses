# Спрощена перевірка циліндричної геозони навколо дому.
# dist_home_m() рахує відстань (метри) від поточної точки до HOME
# за формулою гаверсинусів; тут ми лише порівнюємо її з радіусом.

FENCE_RADIUS_M = 300.0    # радіус «бляшанки», метри
FENCE_ALT_MAX_M = 120.0   # стеля висоти, метри

def inside_cylinder(lat, lon, alt_m):
    d = dist_home_m(lat, lon)         # відстань до дому по горизонталі
    if d > FENCE_RADIUS_M:            # вилетів за коло
        return False
    if alt_m > FENCE_ALT_MAX_M:       # пробив стелю
        return False
    return True                       # усередині і кола, і стелі
