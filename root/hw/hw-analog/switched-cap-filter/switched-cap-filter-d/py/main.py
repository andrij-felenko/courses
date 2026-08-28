# Еквівалентний опір комутованого конденсатора та обернена задача.
# C — у фарадах, f — у герцах, R — в омах.
def sc_resistance(f_clk, c):
    return 1.0 / (f_clk * c)            # R = 1 / (f·C)


def sc_clock_for_resistance(r_target, c):
    return 1.0 / (r_target * c)         # f = 1 / (R·C)


# sc_clock_for_resistance(1.0e6, 1.0e-12) -> 1.0e6 Гц  (1 МГц під 1 МОм)
