import math

class CzochralskiSimulator:
    def __init__(self, target_radius_mm=150.0, target_pull_rate_mm_min=1.2):
        self.target_r = target_radius_mm
        self.target_vp = target_pull_rate_mm_min / 60.0  # мм/с
        self.integral_err = 0.0
        self.prev_err = 0.0

    def step(self, measured_r_mm, dt_s=5.0):
        err = self.target_r - measured_r_mm
        self.integral_err += err * dt_s
        deriv_err = (err - self.prev_err) / dt_s
        self.prev_err = err

        # Коефіцієнти ПІД
        kp, ki, kd = 0.02, 0.0005, 0.003
        delta_vp = -(kp * err + ki * self.integral_err + kd * deriv_err)
        
        vp_mm_s = max(0.1 / 60.0, min(4.0 / 60.0, self.target_vp + delta_vp))
        heater_power_kw = max(50.0, min(150.0, 85.0 - 0.25 * err))

        return vp_mm_s * 60.0, heater_power_kw  # мм/хв, кВт

def main():
    sim = CzochralskiSimulator(target_radius_mm=150.0, target_pull_rate_mm_min=1.2)
    radius = 142.0  # Початковий діаметр 284 мм замість 300 мм
    print("--- Python симуляція контролю діаметра зливка Si ---")
    print("Час (хв) | Діаметр (мм) | v_p (мм/хв) | Потужність (кВт)")

    for t_step in range(21):
        t_min = t_step * 5.0 / 60.0
        vp_mm_min, power_kw = sim.step(radius, dt_s=5.0)
        print(f"{t_min:5.1f} хв | Ø {radius * 2:6.2f} мм | v_p {vp_mm_min:5.3f} мм/хв | P {power_kw:5.1f} кВт")
        radius += (1.2 - vp_mm_min) * 0.15

if __name__ == "__main__":
    main()
