import numpy as np
from scipy.integrate import solve_ivp

def simulate_vdp(eps=0.1, t_max=100.0, dt=0.01):
    # Точна нелінійна система для solve_ivp
    def vdp_sys(t, y):
        x, v = y
        return [v, -x + eps * (1.0 - x**2) * v]

    t_eval = np.arange(0, t_max, dt)
    sol = solve_ivp(vdp_sys, (0, t_max), [1.0, 0.0], t_eval=t_eval, rtol=1e-9, atol=1e-11)
    
    t = sol.t
    x_exact = sol.y[0]
    
    # Перше наближення Боголюбова — Митропольського
    a0 = 1.0
    psi0 = 0.0
    a_t = 2.0 * a0 / np.sqrt(a0**2 + (4.0 - a0**2) * np.exp(-eps * t))
    x_bm1 = a_t * np.cos(t + psi0)
    
    # Друге наближення Боголюбова — Митропольського
    psi_t = psi0 - (eps**2 / 16.0) * t
    theta = t + psi_t
    u1 = - (a_t**3 / 32.0) * np.sin(3.0 * theta)
    x_bm2 = a_t * np.cos(theta) + eps * u1
    
    err1 = np.abs(x_exact - x_bm1)
    err2 = np.abs(x_exact - x_bm2)
    
    print(f"=== Результати Python моделювання для eps = {eps} ===")
    print(f"Максимальна похибка BM-1 (O(eps)):   {np.max(err1):.6f}")
    print(f"Максимальна похибка BM-2 (O(eps^2)): {np.max(err2):.6f}")
    print(f"Коефіцієнт покращення точності:       {np.max(err1)/np.max(err2):.2f}x")
    
    return t, x_exact, x_bm1, x_bm2

if __name__ == "__main__":
    simulate_vdp()
