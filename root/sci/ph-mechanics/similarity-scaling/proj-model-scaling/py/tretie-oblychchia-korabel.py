G = 9.81

def froude_speed(v_full, L_full, scale, water=WATER):
    """Швидкість моделі корабля, що зрівнює число Фруда (хвильовий опір)."""
    L_model  = scale * L_full
    v_model  = v_full * math.sqrt(L_model / L_full)   # рівне Fr → v ∝ √L
    Re_full  = v_full  * L_full  / water.nu
    Re_model = v_model * L_model / water.nu
    return v_model, Re_full, Re_model

def cf_ittc(Re):
    """Коефіцієнт тертя пласкої пластини, стандартна лінія ITTC-1957."""
    return 0.075 / (math.log10(Re) - 2)**2

v_m, Re_s, Re_m = froude_speed(10.0, 150.0, 1/25)   # корабель 150 м, 10 м/с, модель 1:25
print(f"v_моделі = {v_m:.1f} м/с   Re: корабель {Re_s:.2e} → модель {Re_m:.2e}  (×{Re_s/Re_m:.0f} менше)")
