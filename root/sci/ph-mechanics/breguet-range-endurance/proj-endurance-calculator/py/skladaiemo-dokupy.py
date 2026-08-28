def breguet_jet_range(V, LD, c_t, weight_ratio):
    """Гола формула Бреге для реактивної дальності — для перевірок."""
    return V / (G * c_t) * LD * math.log(weight_ratio)


def _self_test():
    # 1) гола формула відтворює хрестоматійний лайнер (~11 600 км)
    assert abs(breguet_jet_range(250, 18, 16e-6, 1.5) - 11.63e6) < 0.1e6
    # 2) три оптимуми задовольняють свої умови балансу опорів
    p = Polar(0.025, 0.045, S=1.0); o = p.optima()
    assert abs(p.k * o["md"] ** 2 / p.CD0 - 1.0) < 1e-9      # індуктивний = паразитний
    assert abs(p.k * o["mp"] ** 2 / p.CD0 - 3.0) < 1e-9      # індуктивний утричі більший
    assert abs(p.k * o["jr"] ** 2 / p.CD0 - 1 / 3) < 1e-9    # паразитний утричі більший
    # 3) дальність акумулятора НЕ залежить від площі крила (лише від L/D)
    a = electric(3.5, 1.0, joules(220), 0.72, Polar(0.030, 0.040, 0.28))
    b = electric(3.5, 1.0, joules(220), 0.72, Polar(0.030, 0.040, 0.60))
    assert abs(a["range_km"] - b["range_km"]) < 1e-6
    print("самоперевірки пройдено")


if __name__ == "__main__":
    _self_test()

    print("\n== електричний БПЛА (3.5 кг, батарея 1.0 кг, 220 Вт·год/кг) ==")
    uav = Polar(CD0=0.030, k=0.040, S=0.28)
    r = electric(m=3.5, m_bat=1.0, e_star=joules(220), eta=0.72, polar=uav)
    print(f"дальність : {r['range_km']:6.0f} км  на V = {r['V_range']:.0f} м/с  (L/D = {r['LDmax']:.1f})")
    print(f"тривалість: {r['endur_h']:6.1f} год на V = {r['V_endur']:.0f} м/с")

    print("\n== вузькофюзеляжний лайнер (70 т, пальне 15 т, крейсер 11 км) ==")
    jet = Polar(CD0=0.022, k=0.038, S=122.6)
    jc = jet_fuel(70000, 15000, c_t=16e-6, polar=jet, reserve=0.05, rho=0.3639)
    ja = jet_fuel(70000, 15000, c_t=16e-6, polar=jet, reserve=0.05, rho=0.3639,
                  cruise_climb=False)
    print(f"дальність (крейсер-набір): {jc['range_km']:6.0f} км  на V = {jc['V_range']:.0f} м/с (L/D = {jc['LD_range']:.1f})")
    print(f"дальність (стала висота) : {ja['range_km']:6.0f} км  — на {100*(jc['range_km']-ja['range_km'])/jc['range_km']:.0f}% менше")
    print(f"тривалість (макс L/D)    : {jc['endur_h']:6.1f} год")
