# Чи можна стикувати дві шини? Лише якщо однакова розрядність.
def widths_match(a, b):
    return bus_width(a) == bus_width(b)

# Сумарна ширина склеювання [частина, частина, ...].
# [CTRL, D[6..0]] → 1 + 7 = 8.
def concat_width(parts):
    return sum(bus_width(p) for p in parts)

# Звірити склеювання з приймачем заданої ширини; інакше — попередити.
def check_concat(parts, sink_width):
    w = concat_width(parts)
    if w != sink_width:
        print(f"ПОМИЛКА розрядності: склеювання дає {w} ліній, "
              f"приймач чекає {sink_width}")
        return False
    return True
