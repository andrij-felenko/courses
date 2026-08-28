# pendulum_sim.py - Обчислення моделі маятника на Python
import math

def simulate_pendulum_rk4(length=1.0, gravity=9.80665, theta0_deg=30.0, dt=0.001, max_time=20.0):
    theta0 = math.radians(theta0_deg)
    theta = theta0
    omega = 0.0
    t = 0.0

    peaks = []
    prev_theta = theta
    prev_prev_theta = theta

    def derivatives(th, om):
        return om, -(gravity / length) * math.sin(th)

    while t < max_time and len(peaks) < 2:
        k1_th, k1_om = derivatives(theta, omega)
        k2_th, k2_om = derivatives(theta + 0.5 * dt * k1_th, omega + 0.5 * dt * k1_om)
        k3_th, k3_om = derivatives(theta + 0.5 * dt * k2_th, omega + 0.5 * dt * k2_om)
        k4_th, k4_om = derivatives(theta + dt * k3_th, omega + dt * k3_om)

        theta += (dt / 6.0) * (k1_th + 2 * k2_th + 2 * k3_th + k4_th)
        omega += (dt / 6.0) * (k1_om + 2 * k2_om + 2 * k3_om + k4_om)
        t += dt

        if prev_theta > 0 and prev_theta >= prev_prev_theta and prev_theta >= theta:
            peaks.append(t - dt)

        prev_prev_theta = prev_theta
        prev_theta = theta

    t_sim = (peaks[1] - peaks[0]) if len(peaks) == 2 else 0.0
    
    t0 = 2 * math.pi * math.sqrt(length / gravity)
    k = math.sin(theta0 / 2)
    t_theory = t0 * (1 + 0.25 * k**2 + (9/64) * k**4 + (225/2304) * k**6)

    return t_sim, t_theory

if __name__ == '__main__':
    print("=== РЕЗУЛЬТАТИ СИМУЛЯЦІЇ (Python) ===")
    for deg in [5.0, 30.0, 60.0, 90.0, 120.0, 150.0]:
        t_sim, t_theory = simulate_pendulum_rk4(theta0_deg=deg)
        err = abs(t_sim - t_theory) / t_theory * 100.0
        print(f"Кут: {deg:5.1f}° | T_симуляція: {t_sim:.5f} c | T_теорія: {t_theory:.5f} c | Похибка: {err:.4f}%")
