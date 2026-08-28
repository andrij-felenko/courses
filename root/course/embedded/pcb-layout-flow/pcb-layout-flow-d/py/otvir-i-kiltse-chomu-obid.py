from dataclasses import dataclass

# Перевірка отвору: чи майданчик тримає кільце й чи затече мідь у діру.
# Розміри — у міліметрах. Числа-допуски — типові для дешевого процесу.
@dataclass
class DrillCheck:
    ring_ok: bool        # майданчик достатній для кільця
    aspect_ok: bool      # мідь надійно осяде в отворі
    ring_nominal: float  # фактичне номінальне кільце
    aspect: float        # співвідношення сторін

def check_hole(pad_d, hole_d, board_thickness,
               ring_min=0.15,   # гарантоване кільце
               misreg=0.05,     # похибка суміщення
               d_tol=0.05,      # розкид діаметра
               ar_limit=10.0):  # межа aspect ratio
    ring_nominal = (pad_d - hole_d) * 0.5
    # потрібне номінальне кільце з урахуванням найгіршого зсуву й розкиду
    ring_needed = ring_min + misreg + d_tol * 0.5
    aspect = board_thickness / hole_d
    return DrillCheck(ring_ok=ring_nominal >= ring_needed,
                      aspect_ok=aspect <= ar_limit,
                      ring_nominal=ring_nominal,
                      aspect=aspect)

# via 0.3мм у майданчику 0.6мм на платі 1.6мм:
#   ring_nominal = (0.6 - 0.3)/2 = 0.15 мм
#   ring_needed  = 0.15 + 0.05 + 0.025 = 0.225 мм  → 0.15 < 0.225 → ЗАМАЛИЙ!
#   aspect       = 1.6 / 0.3 = 5.3 ≤ 10 → ок
# Мораль: «майданчик удвічі більший за отвір» ЗАМАЛО з урахуванням суміщення.
# Треба 0.75 мм, не 0.6. Саме цю помилку EDA-DRC і ловить.
