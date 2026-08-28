// Чи ставити компенсаційний резистор і якого номіналу (0 — не ставити).
// Вирівнювання гасить лише доданок з I_B; якщо I_os того ж порядку,
// гасити нема чого — а зайвий резистор додасть теплового шуму.
static double comp_resistor(const Amp &a, const Circuit &c) {
    if (2.0 * a.ios25 >= a.ib25) return 0.0;
    return std::fabs(c.r_plus - c.r_minus);   // дотягнути «легший» вхід до важчого
}

// Той самий тракт із компенсаційним резистором: обидва входи бачать однаково.
static Circuit balanced(const Circuit &c) {
    double r = std::max(c.r_plus, c.r_minus);
    Circuit b = { r, r, c.noise_gain, c.swing };
    return b;
}

// Скільки дозволено похибки НА ВХОДІ, щоб на виході з'їсти не більше частки LSB.
static double budget_from_adc(double fsr, int bits, double lsb_fraction, double noise_gain) {
    return fsr / std::pow(2.0, bits) * lsb_fraction / noise_gain;
}
