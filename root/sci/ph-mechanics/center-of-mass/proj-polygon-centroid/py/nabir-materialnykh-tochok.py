def center_of_mass(masses, positions):
    """masses[i] — маса i-ї точки; positions[i] — її координати (кортеж
    будь-якої вимірності). Повертає центр мас як кортеж тієї самої вимірності."""
    total = 0.0
    acc = [0.0] * len(positions[0])
    for m, p in zip(masses, positions):
        total += m
        for k, coord in enumerate(p):
            acc[k] += m * coord               # накопичуємо mᵢ·rᵢ по осях
    if total == 0.0:
        raise ValueError("сумарна маса нульова")
    return tuple(a / total for a in acc)      # ділимо один раз наприкінці
