import numpy as np

def schwarzschild_photon_rk4(r_initial, impact_parameter_b, r_s, max_steps=50000, dphi=0.0005):
    """
    Чисельне інтегрування геодезичної ліній фотона у метриці Шварцшильда.
    r_initial — початкова відстань до джерела (м)
    impact_parameter_b — пристрільний параметр (м)
    r_s — шварцшильдівський радіус центральної маси (м)
    """
    u = 1.0 / r_initial
    # Обчислення початкової кутової похідної du/dphi
    w_sq = 1.0 / (impact_parameter_b**2) - (u**2) * (1.0 - r_s * u)
    w = np.sqrt(max(0.0, w_sq))
    
    phi = 0.0
    trajectory = []

    def rhs(u_val, w_val):
        """Праві частини системи рівнянь першого порядку."""
        du_dphi = w_val
        dw_dphi = 1.5 * r_s * (u_val**2) - u_val
        return du_dphi, dw_dphi

    for step in range(max_steps):
        r_current = 1.0 / u if u > 1e-15 else np.inf
        trajectory.append({
            'step': step,
            'phi': phi,
            'r': r_current,
            'u': u,
            'w': w
        })

        # Умова 1: Поглинання чорною дірою (u >= 1/r_s)
        if u >= (1.0 / r_s):
            break

        # Умова 2: Виліт на нескінченність (u <= 0 після проходження перигелію)
        if u <= 0.0 and phi > (np.pi / 2.0):
            break

        # Крок методом Рунге-Кутти 4-го порядку
        k1_u, k1_w = rhs(u, w)
        k2_u, k2_w = rhs(u + 0.5 * dphi * k1_u, w + 0.5 * dphi * k1_w)
        k3_u, k3_w = rhs(u + 0.5 * dphi * k2_u, w + 0.5 * dphi * k2_w)
        k4_u, k4_w = rhs(u + dphi * k3_u, w + dphi * k3_w)

        u += (dphi / 6.0) * (k1_u + 2.0 * k2_u + 2.0 * k3_u + k4_u)
        w += (dphi / 6.0) * (k1_w + 2.0 * k2_w + 2.0 * k3_w + k4_w)
        phi += dphi

    return trajectory

def calculate_deflection_angle(trajectory):
    """Обчислення кута відхилення світла (радіани) за результатом симуляції."""
    if not trajectory:
        return 0.0
    last_point = trajectory[-1]
    # Якщо фотон полетів на нескінченність, кут відхилення theta = |phi_final - pi|
    if last_point['u'] <= 0.0:
        return abs(last_point['phi'] - np.pi)
    return np.nan  # Фотон захоплено чорною дірою

# Демонстраційний розрахунок для Сонця
if __name__ == "__main__":
    r_sun_s = 2950.0       # Гравітаційний радіус Сонця (м)
    radius_sun = 6.96e8    # Радіус Сонця (м)
    
    traj = schwarzschild_photon_rk4(r_initial=1.0e11, impact_parameter_b=radius_sun, r_s=r_sun_s)
    deflection_rad = calculate_deflection_angle(traj)
    deflection_arcsec = deflection_rad * (180.0 / np.pi) * 3600.0 if not np.isnan(deflection_rad) else 0.0

    print(f"Обраховано {len(traj)} точок геодезичної траєкторії.")
    print(f"Розрахований кут відхилення світла біля краю Сонця: {deflection_arcsec:.3f} кутових секунд.")
