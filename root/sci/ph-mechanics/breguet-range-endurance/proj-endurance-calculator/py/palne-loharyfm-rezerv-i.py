def prop_fuel(m, m_fuel, e_star, eta, polar, reserve=0.0, rho=RHO_SL):
    """Гвинтовий на пальному: вага ТАНЕ → логарифм для дальності."""
    m_use = m_fuel * (1.0 - reserve)    # резерв не спалюємо — рахує лише робоче пальне
    W0, W1 = m * G, (m - m_use) * G     # повний бак → сухий
    o = polar.optima()

    LDmax = polar.LD(o["md"])
    R = (eta * e_star / G) * LDmax * math.log(W0 / W1)          # дальність: чистий ln

    P32 = o["mp"] ** 1.5 / polar.CD(o["mp"])                    # (CL^1.5/CD)max
    t = (eta * e_star / G) * P32 * math.sqrt(2 * rho * polar.S) \
        * (1.0 / math.sqrt(W1) - 1.0 / math.sqrt(W0))          # тривалість: різниця 1/√W
    return {"range_km": R / 1e3, "endur_h": t / 3600.0,
            "V_range": polar.speed(o["md"], W0, rho),
            "V_endur": polar.speed(o["mp"], W0, rho)}


def jet_fuel(m, m_fuel, c_t, polar, reserve=0.0, rho=RHO_SL, cruise_climb=True):
    """Реактивний: палить за тягу. Дальність на макс CL^0.5/CD, тривалість на макс L/D."""
    m_use = m_fuel * (1.0 - reserve)
    W0, W1 = m * G, (m - m_use) * G
    o = polar.optima()
    LDmax, LD_jr = polar.LD(o["md"]), polar.LD(o["jr"])
    V0 = polar.speed(o["jr"], W0, rho)                          # оптимальна швидкість дальності

    if cruise_climb:                                           # сталі CL і V, апарат «спливає»
        R = (V0 / (G * c_t)) * LD_jr * math.log(W0 / W1)       # → чистий ln
    else:                                                      # стала висота: V падає з вагою
        R = (2.0 / (G * c_t)) * math.sqrt(2.0 / (rho * polar.S)) \
            * (math.sqrt(o["jr"]) / polar.CD(o["jr"])) * (math.sqrt(W0) - math.sqrt(W1))

    E = (1.0 / (G * c_t)) * LDmax * math.log(W0 / W1)          # тривалість: макс L/D, чистий ln
    return {"range_km": R / 1e3, "endur_h": E / 3600.0,
            "V_range": V0, "LD_range": LD_jr, "LDmax": LDmax}
