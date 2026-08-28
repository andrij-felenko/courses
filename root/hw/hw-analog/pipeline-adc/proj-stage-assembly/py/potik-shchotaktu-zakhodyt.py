# Потоковий цикл: щотакту одні свіжі цифри входять, один готовий код виходить.
# samples — вхідні відліки; на кожен ми моделюємо аналогову частину (stage_15bit),
# а бек-енд вирівнює й складає. У реальному приладі raw і final2 приходять із заліза.
def run_stream(samples):
    be = Backend()
    codes_out = []

    for v in samples:
        # ── аналогова частина: прогнати відлік крізь щаблі, зібрати сирі цифри ──
        raw = [0] * NSTAGE
        for s in range(NSTAGE):
            raw[s], v = stage_15bit(v, 0)          # у житті — з заліза
        # хвіст-flash: залишок останнього щабля → 2 біти
        VREF = 1 << 15
        q = ((v + VREF) * 4) // (2 * VREF)
        final2 = 0 if q < 0 else 3 if q > 3 else q

        # ── цифровий бек-енд: вирівняти в часі й скласти ──
        valid, code = be_step(be, raw, final2)
        if valid:
            codes_out.append(code)                 # код відліку, що зайшов LAT тактів тому

    return codes_out
