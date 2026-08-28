# phase_plotter.py — Побудова векторного поля та граничного циклу мовою Python (SciPy / Matplotlib)
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Рівняння осцилятора Ван дер Поля: dq/dt = p, dp/dt = mu * (1 - q^2) * p - q
def van_der_pol(t, state, mu=1.5):
    q, p = state
    return [p, mu * (1.0 - q**2) * p - q]

# Створення сітки фазового простору
q_grid, p_grid = np.mgrid[-3.5:3.5:25j, -3.5:3.5:25j]
dq_dt = p_grid
dp_dt = 1.5 * (1.0 - q_grid**2) * p_grid - q_grid
speed = np.hypot(dq_dt, dp_dt)

plt.figure(figsize=(9, 7))

# Малювання фазового векторного поля (векторних струменів)
plt.streamplot(q_grid, p_grid, dq_dt, dp_dt, color=speed, cmap='plasma', density=1.2, linewidth=1.1)

# Інтегрування траєкторії зсередини (зростання)
sol_in = solve_ivp(van_der_pol, [0, 25], [0.1, 0.1], t_eval=np.linspace(0, 25, 1000))
plt.plot(sol_in.y[0], sol_in.y[1], color='#2457d6', linewidth=2.0, label='Траєкторія зсередини')

# Інтегрування траєкторії ззовні (спадання)
sol_out = solve_ivp(van_der_pol, [0, 25], [3.0, 2.5], t_eval=np.linspace(0, 25, 1000))
plt.plot(sol_out.y[0], sol_out.y[1], color='#c0392b', linewidth=2.0, label='Траєкторія ззовні')

plt.title('Фазовий портрет осцилятора Ван дер Поля (стійкий граничний цикл)')
plt.xlabel('Координата q')
plt.ylabel('Імпульс / швидкість p')
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend()
plt.tight_layout()
plt.savefig('van_der_pol_phase.png', dpi=300)
plt.show()
