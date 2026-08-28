def raw_to_level(raw):
    # нижче першої точки — вважаємо мінімальним рівнем
    if raw <= CAL_TABLE[0][0]:
        return CAL_TABLE[0][1]
    # вище останньої — максимальним
    if raw >= CAL_TABLE[-1][0]:
        return CAL_TABLE[-1][1]

    # шукаємо відрізок [i, i+1], у який потрапив raw
    for i in range(len(CAL_TABLE) - 1):
        r0, l0 = CAL_TABLE[i]
        r1, l1 = CAL_TABLE[i + 1]
        if r0 <= raw <= r1:
            # лінійна інтерполяція ВСЕРЕДИНІ відрізка (int — точна арифметика)
            return l0 + (raw - r0) * (l1 - l0) // (r1 - r0)
    return CAL_TABLE[-1][1]  # недосяжно
