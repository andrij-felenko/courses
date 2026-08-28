import math

# Скільки паралельних via треба, щоб провести струм target_a при перегріві dT.
#   target_a  — потрібний струм крізь групу via, А
#   drill_mm, plating_um — геометрія одного отвору
#   delta_t_c — допустимий перегрів, °C
#   external  — модель охолодження via (див. via_current_a)
#   margin    — запас часток (0.15 = +15% отворів на нерівний розподіл струму)
# Повертає кількість via (ціле, вже із запасом), або -1 при некоректних аргументах.
def via_count_for_current(target_a, drill_mm, plating_um,
                          delta_t_c, external, margin):
    if target_a <= 0.0 or margin < 0.0:
        return -1

    per_via = via_current_a(drill_mm, plating_um, delta_t_c, external)
    if per_via <= 0.0:
        return -1                          # помилка розмірів або dT

    # Скільки треба «в лоб»: округлити ВГОРУ (пів-via не буває).
    raw = math.ceil(target_a / per_via)

    # Додати запас на нерівний розподіл струму й округлити вгору знову.
    n = math.ceil(raw * (1.0 + margin))
    return 1 if n < 1 else n               # хоч один via завжди потрібен
