HC = 1239.84198     # E(еВ) = HC / λ(нм)

def am15_photons_above(Eg, wl, irr):
    """Фотони/с/м² з таблиці AM1.5G (λ у нм, irr у Вт/м²/нм) з E ≥ Eg,
    тобто з λ ≤ HC/Eg. Потужність ділимо на енергію фотона → потік."""
    lam_max, total = HC/Eg, 0.0
    for i in range(len(wl) - 1):
        if wl[i] > lam_max:
            break
        E_J   = (HC/wl[i]) * q          # енергія фотона, Дж
        total += (irr[i] / E_J) * (wl[i+1] - wl[i])
        # ↑ (Вт/м²/нм)/(Дж/фотон) · нм = фотони/с/м²
    return total
