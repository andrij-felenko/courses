// Еквівалентний опір комутованого конденсатора та обернена задача.
// C — у фарадах, f — у герцах, R — в омах.
float sc_resistance(float f_clk, float c)
{
    return 1.0f / (f_clk * c);          // R = 1 / (f·C)
}

float sc_clock_for_resistance(float r_target, float c)
{
    return 1.0f / (r_target * c);       // f = 1 / (R·C)
}
// sc_clock_for_resistance(1.0e6f, 1.0e-12f) -> 1.0e6 Гц  (1 МГц під 1 МОм)
