def comp_resistor(a: Amp, c: Circuit) -> float:
    """Чи ставити компенсаційний резистор і якого номіналу (0 — не ставити).
    Вирівнювання гасить лише доданок з I_B; якщо I_os того ж порядку,
    гасити нема чого — а зайвий резистор додасть теплового шуму."""
    if 2.0 * a.ios25 >= a.ib25:
        return 0.0
    return abs(c.r_plus - c.r_minus)      # дотягнути «легший» вхід до важчого


def balanced(c: Circuit) -> Circuit:
    """Той самий тракт із компенсаційним резистором: обидва входи бачать однаково."""
    r = max(c.r_plus, c.r_minus)
    return Circuit(r, r, c.noise_gain, c.swing)


def budget_from_adc(fsr: float, bits: int, lsb_fraction: float, noise_gain: float) -> float:
    """Скільки дозволено похибки НА ВХОДІ, щоб на виході з'їсти не більше частки LSB."""
    return fsr / 2 ** bits * lsb_fraction / noise_gain
