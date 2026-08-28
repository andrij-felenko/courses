def recover(I_meas, eta_meas):
    """З виміряних (I, η) відновити (P_фікс, k, R) моделі втрат."""
    I_meas   = np.asarray(I_meas, float)
    eta_meas = np.asarray(eta_meas, float)
    # крок-ключ: з кожної точки дістаємо ВТРАТИ на цьому струмі
    p_loss_meas = V_out * I_meas * (1.0 - eta_meas) / eta_meas
    # P_втрат = P_фікс·1 + k·I + R·I²  — лінійно за невідомими
    A = np.column_stack([np.ones_like(I_meas), I_meas, I_meas**2])
    if len(I_meas) == 3:
        return np.linalg.solve(A, p_loss_meas)                    # точна система
    coeffs, *_ = np.linalg.lstsq(A, p_loss_meas, rcond=None)      # МНК
    return coeffs

# три точки, «як із даташита» — беремо їх із самої моделі (повна точність)
I3   = np.array([0.03, 0.387, 3.0])
eta3 = efficiency(I3)
P_fix_r, k_r, R_r = recover(I3, eta3)
print(f"відновлено:  P_фікс = {P_fix_r:.4f} Вт   k = {k_r:.4f} Вт/А   R = {R_r:.4f} Ом")
