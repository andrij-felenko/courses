def electric(m, m_bat, e_star, eta, polar, rho=RHO_SL):
    """Акумулятор: вага СТАЛА (батарея не легшає) → дальність без логарифма."""
    W     = m * G                       # ← вага, а не маса: множимо на g
    E_use = eta * e_star * m_bat        # корисні джоулі, що дійдуть до повітря
    o     = polar.optima()

    # найдальше — на швидкості найбільшої якості; дальність від швидкості НЕ залежить
    LDmax = polar.LD(o["md"])
    R     = E_use / W * LDmax           # = e*·(m_bat/m)·η·(L/D)/g

    # найдовше — на швидкості найменшої потужності
    V_e   = polar.speed(o["mp"], W, rho)
    P_min = W * V_e / polar.LD(o["mp"]) # потрібна потужність = опір·швидкість
    t     = E_use / P_min
    return {"range_km": R / 1e3, "V_range": polar.speed(o["md"], W, rho),
            "endur_h": t / 3600.0, "V_endur": V_e, "LDmax": LDmax}
