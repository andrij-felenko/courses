import math

class MOSInversionSimulator:
    """
    Чисельний розв'язувач рівняння Пуассона-Больцмана для МДН-структури.
    Обчислює поверхневий потенціал, просторовий профіль psi(x), n(x), p(x)
    та інтегральний інверсійний заряд Q_n.
    """
    # Елементарні фізичні константи (СІ)
    Q_ELEM = 1.602176634e-19    # Кулон
    KB = 1.380649e-23           # Дж/К
    EPS0 = 8.8541878128e-14     # Ф/см (питома проникність вакууму)
    EPS_SI = 11.7 * EPS0        # Кремній
    EPS_OX = 3.9 * EPS0         # Dioxyd SiO2
    N_I = 1.5e10                # Власна концентрація Si при 300K, см^-3

    def __init__(self, v_g=2.5, n_a=1e16, d_ox_nm=5.0, temp_k=300.0, v_fb=0.0):
        self.v_g = v_g
        self.n_a = n_a
        self.d_ox_cm = d_ox_nm * 1e-7
        self.temp_k = temp_k
        self.v_fb = v_fb

        self.vt = (self.KB * temp_k) / self.Q_ELEM
        self.psi_b = self.vt * math.log(n_a / self.N_I)
        self.c_ox = self.EPS_OX / self.d_ox_cm
        self.l_d = math.sqrt((self.EPS_SI * self.vt) / (2.0 * self.Q_ELEM * n_a))

    def _kingston_neustadter_f(self, psi_s):
        """Обчислення функції F(u_s) та поверхневого поля F_s (В/см)"""
        if psi_s <= 0:
            return 0.0
        u_s = psi_s / self.vt
        ratio = self.N_I / self.n_a
        term1 = math.exp(-u_s) + u_s - 1.0
        term2 = (ratio ** 2) * (math.exp(u_s) - u_s - 1.0)
        f_val = math.sqrt(max(0.0, term1 + term2))
        return (math.sqrt(2.0) * self.vt / self.l_d) * f_val

    def _gate_residual(self, psi_s):
        """Нелінійне рівняння балансу напруг: g(psi_s) = 0"""
        f_s = self._kingston_neustadter_f(psi_s)
        q_sc = -self.EPS_SI * f_s
        v_g_calc = self.v_fb + psi_s + (abs(q_sc) / self.c_ox)
        return v_g_calc - self.v_g

    def solve_surface_potential(self):
        """Метод бісекції для знаходження поверхневого потенціалу psi_s"""
        low, high = 0.0001, max(0.1, self.v_g)
        for _ in range(80):
            mid = (low + high) / 2.0
            res = self._gate_residual(mid)
            if res > 0:
                high = mid
            else:
                low = mid
        return (low + high) / 2.0

    def run_simulation(self, x_max_nm=20.0, dx_nm=0.05):
        """Повний прогін чисельного інтегрування методом RK4"""
        psi_s = self.solve_surface_potential()
        f_s_init = self._kingston_neustadter_f(psi_s)

        dx_cm = dx_nm * 1e-7
        n_steps = int(x_max_nm / dx_nm)

        x_coords = []
        psi_profile = []
        n_profile = []
        p_profile = []

        curr_psi = psi_s
        curr_f = f_s_init

        def rhs_psi(f):
            return -f

        def rhs_f(psi):
            if psi <= 0:
                return 0.0
            u = psi / self.vt
            p_conc = self.n_a * math.exp(-u)
            n_conc = ((self.N_I ** 2) / self.n_a) * math.exp(u)
            rho = self.Q_ELEM * (p_conc - n_conc - self.n_a)
            return -rho / self.EPS_SI

        for i in range(n_steps + 1):
            x_nm = i * dx_nm
            x_coords.append(x_nm)
            psi_profile.append(curr_psi)

            u = curr_psi / self.vt if curr_psi > 0 else 0.0
            n_val = ((self.N_I ** 2) / self.n_a) * math.exp(u)
            p_val = self.n_a * math.exp(-u) if curr_psi > 0 else self.n_a
            n_profile.append(n_val)
            p_profile.append(p_val)

            # Крок методa Рунге-Кутти 4-го порядку для системи (psi, F)
            k1_psi = rhs_psi(curr_f)
            k1_f = rhs_f(curr_psi)

            k2_psi = rhs_psi(curr_f + 0.5 * dx_cm * k1_f)
            k2_f = rhs_f(curr_psi + 0.5 * dx_cm * k1_psi)

            k3_psi = rhs_psi(curr_f + 0.5 * dx_cm * k2_f)
            k3_f = rhs_f(curr_psi + 0.5 * dx_cm * k2_psi)

            k4_psi = rhs_psi(curr_f + dx_cm * k3_f)
            k4_f = rhs_f(curr_psi + dx_cm * k3_psi)

            curr_psi += (dx_cm / 6.0) * (k1_psi + 2*k2_psi + 2*k3_psi + k4_psi)
            curr_f += (dx_cm / 6.0) * (k1_f + 2*k2_f + 2*k3_f + k4_f)

            if curr_psi < 0:
                curr_psi = 0.0

        # Обчислення інверсійного заряду Q_n (метод трапецій)
        q_n_total = 0.0
        n_0 = (self.N_I ** 2) / self.n_a
        for i in range(len(n_profile) - 1):
            if n_profile[i] > self.n_a:
                avg_n = 0.5 * (n_profile[i] + n_profile[i+1]) - n_0
                q_n_total += self.Q_ELEM * avg_n * dx_cm

        return {
            "psi_s": psi_s,
            "psi_b": self.psi_b,
            "q_n": q_n_total,
            "x_nm": x_coords,
            "psi": psi_profile,
            "n": n_profile,
            "p": p_profile
        }

if __name__ == "__main__":
    sim = MOSInversionSimulator(v_g=2.5, n_a=1e16, d_ox_nm=5.0)
    res = sim.run_simulation()

    print(f"--- Результати симуляції (Python) ---")
    print(f"Поверхневий потенціал psi_s = {res['psi_s']:.4f} В")
    print(f"Об'ємний потенціал Фермі psi_b = {res['psi_b']:.4f} В")
    print(f"Поріг сильної інверсії 2*psi_b = {2 * res['psi_b']:.4f} В")
    print(f"Інверсійний заряд Q_n = {res['q_n']:.4e} Кл/см²")
    print("\nПрофіль потенціалу біля поверхні:")
    for x, psi, n in zip(res['x_nm'][:6], res['psi'][:6], res['n'][:6]):
        print(f"  x = {x:.2f} нм: ψ = {psi:.4f} В, n = {n:.3e} см⁻³")
