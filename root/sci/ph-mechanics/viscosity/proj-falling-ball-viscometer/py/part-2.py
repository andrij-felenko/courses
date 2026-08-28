r     = 1.0e-3     # радіус кульки, м       (діаметр 2 мм)
R     = 12.5e-3    # внутрішній радіус трубки, м  (діаметр 25 мм)
rho_s = 7850.0     # хромована сталь, кг/м³
rho_f = 1260.0     # гліцерин при 20 °C, кг/м³

v_meas  = 0.100 / 8.13                          # усталена швидкість у трубці, м/с
mu_app  = stokes_viscosity(r, rho_s, rho_f, v_meas)
L       = wall_factor(r, R)
mu_corr = mu_app / L                            # прибираємо пристінкове гальмо
Re      = reynolds(r, rho_f, v_meas, mu_corr)

print(f"v_виміряна      = {v_meas*100:.2f} см/с")
print(f"μ (сира)        = {mu_app:.3f} Па·с   ← ще з пристінковим гальмом")
print(f"r/R = {r/R:.3f}   L = {L:.3f}")
print(f"μ (з поправкою) = {mu_corr:.3f} Па·с")
print(f"Re              = {Re:.4f}")
