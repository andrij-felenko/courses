import math

class VanDerWaalsGas:
    R = 8.314462618  # Дж / (моль · К)

    def __init__(self, name: str, a: float, b: float):
        """
        a: Па · м^6 / моль^2
        b: м^3 / моль
        """
        self.name = name
        self.a = a
        self.b = b

    @property
    def critical_params(self):
        v_c = 3.0 * self.b
        p_c = self.a / (27.0 * self.b**2)
        t_c = (8.0 * self.a) / (27.0 * self.R * self.b)
        z_c = (p_c * v_c) / (self.R * t_c)
        return {"V_c": v_c, "P_c": p_c, "T_c": t_c, "Z_c": z_c}

    def calculate_pressure(self, v_m: float, t: float) -> float:
        """Обчислення тиску P за заданим молярним об'ємом V_m та температурою T."""
        if v_m <= self.b:
            raise ValueError("Молярний об'єм V_m повинен бути більшим за ко-об'єм b")
        return (self.R * t) / (v_m - self.b) - self.a / (v_m**2)

    def solve_volume(self, p: float, t: float) -> list[float]:
        """
        Чисельне розв'язання кубічного рівняння стану відносно V_m:
        P * V_m^3 - (P*b + R*T) * V_m^2 + a * V_m - a*b = 0
        """
        a2 = -(self.b + (self.R * t) / p)
        a1 = self.a / p
        a0 = -(self.a * self.b) / p

        q = (3.0 * a1 - a2**2) / 9.0
        r = (9.0 * a2 * a1 - 27.0 * a0 - 2.0 * a2**3) / 54.0
        discriminant = q**3 + r**2

        roots = []
        if discriminant > 0:
            s = math.cbrt(r + math.sqrt(discriminant))
            t_val = math.cbrt(r - math.sqrt(discriminant))
            v1 = s + t_val - a2 / 3.0
            roots.append(v1)
        else:
            theta = math.acos(r / math.sqrt(-(q**3)))
            sqrt_q = math.sqrt(-q)
            v1 = 2.0 * sqrt_q * math.cos(theta / 3.0) - a2 / 3.0
            v2 = 2.0 * sqrt_q * math.cos((theta + 2.0 * math.pi) / 3.0) - a2 / 3.0
            v3 = 2.0 * sqrt_q * math.cos((theta + 4.0 * math.pi) / 3.0) - a2 / 3.0
            roots = sorted([v1, v2, v3])

        return roots

    def maxwell_construction(self, t: float, num_steps: int = 1000) -> tuple[float, float, float]:
        """
        Знаходження тиску насиченої пари P_sat методом бісекції (пряма Максвелла).
        Повертає (P_sat, V_liquid, V_gas).
        """
        crit = self.critical_params
        if t >= crit["T_c"]:
            raise ValueError("Пряма Максвелла існує лише для підкритичних температур (T < T_c)")

        p_low = 1000.0
        p_high = crit["P_c"] * 0.999

        for _ in range(60):
            p_mid = (p_low + p_high) / 2.0
            roots = self.solve_volume(p_mid, t)

            if len(roots) < 3:
                p_high = p_mid
                continue

            v1, _, v3 = roots
            dv = (v3 - v1) / num_steps
            integral = 0.0
            for i in range(num_steps):
                v_curr = v1 + (i + 0.5) * dv
                p_vdw = self.calculate_pressure(v_curr, t)
                integral += (p_vdw - p_mid) * dv

            if integral > 0:
                p_low = p_mid
            else:
                p_high = p_mid

        p_sat = (p_low + p_high) / 2.0
        final_roots = self.solve_volume(p_sat, t)
        return p_sat, final_roots[0], final_roots[-1]

if __name__ == "__main__":
    co2 = VanDerWaalsGas("Вуглекислий газ (CO2)", a=0.3643, b=4.267e-5)
    crit = co2.critical_params

    print(f"=== КРИТИЧНІ ПАРАМЕТРИ {co2.name} ===")
    print(f"T_c = {crit['T_c'] - 273.15:.2f} °C ({crit['T_c']:.2f} K)")
    print(f"P_c = {crit['P_c'] / 1e5:.2f} бар ({crit['P_c']:.0f} Па)")
    print(f"V_c = {crit['V_c'] * 1e6:.2f} см^3/моль")
    print(f"Z_c = {crit['Z_c']:.4f}\n")

    t_sub = 290.0
    p_sat, v_l, v_g = co2.maxwell_construction(t_sub)
    print(f"=== ФАЗОВА РІВНОВАГА ЗА T = {t_sub} K ===")
    print(f"Тиск насиченої пари P_sat = {p_sat / 1e5:.3f} бар")
    print(f"Молярний об'єм насиченої рідини V_l = {v_l * 1e6:.2f} см^3/моль")
    print(f"Молярний об'єм насиченої пари   V_g = {v_g * 1e6:.2f} см^3/моль")
