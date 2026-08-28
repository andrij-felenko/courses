def eng(v: float, units) -> str:
    a = abs(v)
    for scale, unit in units:
        if a >= scale:
            return "%.1f %s" % (v / scale, unit)
    return "0 " + units[-1][1]

VOLT = ((1.0, "В"), (1e-3, "мВ"), (1e-6, "мкВ"), (1e-9, "нВ"), (1e-12, "пВ"))
OHM  = ((1e9, "ГОм"), (1e6, "МОм"), (1e3, "кОм"), (1.0, "Ом"))


def report(amps, c: Circuit, tmin: float, tmax: float, budget: float, title: str):
    print("%s: R⁺ = %s, R⁻ = %s, %g…%g °C, бюджет на вході %s"
          % (title, eng(c.r_plus, OHM), eng(c.r_minus, OHM), tmin, tmax, eng(budget, VOLT)))
    print("    %-11s %9s %9s %9s %9s   вирок"
          % ("прилад", "V_os", "струм·R", "дрейф", "разом"))

    for e, a in sorted(((worst_case(a, c, tmin, tmax), a) for a in amps),
                       key=lambda p: p[0].total()):
        if (e.vos + e.cur) * c.noise_gain > c.swing:
            verdict = "вихід у насиченні — схема не працює"
        elif e.total() <= budget:
            verdict = "проходить як є"
        elif e.cur + e.drift <= budget:
            verdict = "треба калібрувати нуль приладу"
        elif e.drift <= budget:
            verdict = "треба калібрувати в зборі з датчиком"
        else:
            verdict = "не проходить: ×%.0f над бюджетом" % (e.total() / budget)
        rc = comp_resistor(a, c)
        print("    %-11s %9s %9s %9s %9s   %s%s"
              % (a.name, eng(e.vos, VOLT), eng(e.cur, VOLT), eng(e.drift, VOLT),
                 eng(e.total(), VOLT), verdict,
                 "; спробуй Rc = %s" % eng(rc, OHM) if rc > 0.0 else ""))
    print()


AMPS = [
    #        назва      V_os     TC V_os    I_B       I_os     T_flat
    Amp("µA741",        6e-3,    20e-6,    500e-9,   200e-9,   math.inf),
    Amp("OP07E",       75e-6,     1.3e-6,    4e-9,     3.8e-9, math.inf),
    Amp("LF356",       10e-3,     5e-6,    200e-12,   50e-12,  25.0),
    Amp("OPA333",      10e-6,     0.05e-6, 200e-12,  400e-12,  85.0),
    Amp("ADA4530-1",   50e-6,     0.13e-6,  20e-15,   40e-15,  85.0),
]

if __name__ == "__main__":
    # 1. pH-метр: скляний електрод 200 МОм на повторювачі, 0…50 °C,
    #    бюджет 0.01 pH = 0.01 · 59.16 мВ/pH.
    ph = Circuit(r_plus=200e6, r_minus=0.0)
    report(AMPS, ph, 0.0, 50.0, 0.01 * 59.16e-3, "pH-метр")

    # 2. Термопара K: 50 Ом з обох боків, підсилення 100, 0…60 °C,
    #    бюджет 0.5 °C = 0.5 · 41 мкВ/°C.
    tc = Circuit(r_plus=50.0, r_minus=50.0, noise_gain=100.0, swing=4.0)
    report(AMPS, tc, 0.0, 60.0, 0.5 * 41e-6, "Термопара K")

    # 3. Буфер ×1 перед 16-бітним АЦП, джерело 10 кОм: бюджет задає чверть LSB.
    buf = Circuit(r_plus=10e3, r_minus=10e3, noise_gain=1.0, swing=4.0)
    report(AMPS, buf, 0.0, 60.0,
           budget_from_adc(4.096, 16, 0.25, buf.noise_gain), "Буфер 10 кОм перед 16-бітним АЦП")

    # 4. Датчик 1 МОм на неінвертувальному ×10 (R⁻ = 10к ‖ 90к = 9 кОм), 25…85 °C.
    raw = Circuit(r_plus=1e6, r_minus=9e3, noise_gain=10.0)
    report(AMPS, raw, 25.0, 85.0, 1e-3, "Датчик 1 МОм, опори НЕ зрівняні")
    report(AMPS, balanced(raw), 25.0, 85.0, 1e-3, "Датчик 1 МОм, опори зрівняні")
