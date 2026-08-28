def resonance_peak(zeta: float) -> tuple[float, float]:
    """(r_peak, T_peak) — де і наскільки T максимальний на розгоні.

    Точний максимум кривої: r_peak = √(√(1 + 8ζ²) − 1) / (2ζ).
    Правило-прикидка: T_peak ≈ 1/(2ζ) для слабкого загасання.
    """
    if zeta <= 0.0:
        return 1.0, float("inf")
    r_peak = sqrt(sqrt(1.0 + 8.0 * zeta * zeta) - 1.0) / (2.0 * zeta)
    return r_peak, transmissibility(r_peak, zeta)
