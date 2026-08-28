import math
import numpy as np

def diode_current(v: float, v_p: float = 0.07, i_p: float = 0.005,
                  v_v: float = 0.35, i_v: float = 0.0005, alpha: float = 10.0) -> float:
    """Аналітична ВАХ тунельного діода (тунельний + дифузійний струм)."""
    if v < 0:
        return -i_p * (abs(v) / v_p)
    i_tunnel = i_p * (v / v_p) * math.exp(1.0 - v / v_p)
    i_diff = i_v * math.exp(alpha * (v - v_v)) if v > v_v else 0.0
    return i_tunnel + i_diff

def derivatives(v: float, i_l: float, v_cc: float, r_l: float,
                l_ind: float, c_cap: float) -> tuple[float, float]:
    """Прави частини систем диференціальних рівнянь (похідні dv/dt та di/dt)."""
    dv_dt = (i_l - diode_current(v)) / c_cap
    di_dt = (v_cc - v - r_l * i_l) / l_ind
    return dv_dt, di_dt

def simulate_ndr_oscillator(v_cc=0.18, r_l=2.0, l_ind=1e-6, c_cap=100e-12,
                             dt=1e-11, steps=20000):
    """Симуляція генератора методом Рунге-Кутти 4-го порядку (RK4)."""
    t_arr = np.zeros(steps)
    v_arr = np.zeros(steps)
    i_arr = np.zeros(steps)

    # Початкові умови (стан близький до точки спокою)
    v, i_l = 0.01, 0.001

    for step in range(steps):
        t_arr[step] = step * dt
        v_arr[step] = v
        i_arr[step] = i_l

        # Коефіцієнти RK4
        kv1, ki1 = derivatives(v, i_l, v_cc, r_l, l_ind, c_cap)
        kv2, ki2 = derivatives(v + 0.5*dt*kv1, i_l + 0.5*dt*ki1, v_cc, r_l, l_ind, c_cap)
        kv3, ki3 = derivatives(v + 0.5*dt*kv2, i_l + 0.5*dt*ki2, v_cc, r_l, l_ind, c_cap)
        kv4, ki4 = derivatives(v + dt*kv3, i_l + dt*ki3, v_cc, r_l, l_ind, c_cap)

        v += (dt / 6.0) * (kv1 + 2.0*kv2 + 2.0*kv3 + kv4)
        i_l += (dt / 6.0) * (ki1 + 2.0*ki2 + 2.0*ki3 + ki4)

    return t_arr, v_arr, i_arr

if __name__ == "__main__":
    t, v, i = simulate_ndr_oscillator()
    print(f"Симуляція успішна. Кінцева напруга: {v[-1]*1000:.2f} мВ, струм: {i[-1]*1000:.2f} мА")
