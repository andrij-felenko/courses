import math

# ── Фізичні фундаментальні константи ──────────────────────────────────────────
K_B_KEV = 8.617333e-8          # Стала Больцмана (кЕв / Кельвін)
COULOMB_CONST_KEV_FM = 1439.96  # Електростатична стала e^2 / (4pi eps0) (кЕв * фм)
R0_FM = 1.25                    # Ефективний радіус нуклона (фм)
AMU_MEV = 931.494               # Енергетичний еквівалент 1 а.о.м. (МеВ)

class CoulombBarrierSimulator:
    """
    Клас для розрахунку характеристик кулонівського бар'єра,
    тунельної прозорості та піку Ґамова для довільної ядерної реакції.
    """
    def __init__(self, z1: int, a1: float, z2: int, a2: float):
        self.z1 = z1
        self.a1 = a1
        self.z2 = z2
        self.a2 = a2
        
        # Обчислення зведеної маси (а.о.м.)
        self.mu_amu = (a1 * a2) / (a1 + a2)
        
        # Обчислення радіуса зіткнення ядер (фм)
        self.r_collision_fm = R0_FM * (math.pow(a1, 1/3) + math.pow(a2, 1/3))
        
        # Висота кулонівського бар'єра (кЕв та МеВ)
        self.v_barrier_kev = (z1 * z2 * COULOMB_CONST_KEV_FM) / self.r_collision_fm
        self.v_barrier_mev = self.v_barrier_kev / 1000.0
        
        # Астрофізична стала Ґамова b_G (кЕв^(1/2))
        self.b_gamow = 31.291 * z1 * z2 * math.sqrt(self.mu_amu)

    def calculate_gamow_peak(self, temp_kelvin: float) -> dict:
        """
        Обчислює аналітичні та чисельні характеристики піку Ґамова при заданій температурі.
        """
        kb_t_kev = K_B_KEV * temp_kelvin
        
        # Аналітична енергія вершини піку Ґамова (кЕв)
        e0_theory_kev = math.pow((self.b_gamow * kb_t_kev) / 2.0, 2.0 / 3.0)
        
        # Аналітична ширина вікна Ґамова (кЕв)
        delta_e_kev = 4.0 * math.sqrt((e0_theory_kev * kb_t_kev) / 3.0)
        
        # Діапазон чисельного інтегрування навколо E0
        e_min = max(0.01, e0_theory_kev - 3.5 * delta_e_kev)
        e_max = e0_theory_kev + 4.5 * delta_e_kev
        steps = 2000
        de = (e_max - e_min) / steps
        
        max_val = 0.0
        e0_numerical = e0_theory_kev
        integral_sum = 0.0
        
        for i in range(steps + 1):
            e_val = e_min + i * de
            
            # Логарифм інтегранда для запобігання чисельного антипереповнення
            log_integrand = math.log(e_val) - (e_val / kb_t_kev) - (self.b_gamow / math.sqrt(e_val))
            
            if log_integrand > -300.0:
                val = math.exp(log_integrand)
            else:
                val = 0.0
                
            if val > max_val:
                max_val = val
                e0_numerical = e_val
                
            weight = 0.5 if (i == 0 or i == steps) else 1.0
            integral_sum += val * weight * de

        # Прозорість бар'єра при енергії піку E0
        p_at_e0 = math.exp(-self.b_gamow / math.sqrt(e0_numerical))
        
        # Безрозмірний показник подавлення tau
        tau = 3.0 * e0_numerical / kb_t_kev

        return {
            "temp_kelvin": temp_kelvin,
            "kb_t_kev": kb_t_kev,
            "e0_theory_kev": e0_theory_kev,
            "e0_numerical_kev": e0_numerical,
            "delta_e_kev": delta_e_kev,
            "p_at_e0": p_at_e0,
            "tau": tau,
            "integral_rate": integral_sum
        }


def print_simulation_report(reaction_name: str, sim: CoulombBarrierSimulator, temp_k: float):
    res = sim.calculate_gamow_peak(temp_k)
    print(f"=== {reaction_name} (T = {temp_k/1e6:.1f} млн К) ===")
    print(f" Зведена маса μ:             {sim.mu_amu:.4f} а.о.м.")
    print(f" Радіус зіткнення R:         {sim.r_collision_fm:.3f} фм")
    print(f" Висота бар'єра V_B:         {sim.v_barrier_mev:.3f} МеВ ({sim.v_barrier_kev:.1f} кЕв)")
    print(f" Стала Ґамова b_G:           {sim.b_gamow:.2f} кЕв¹/²")
    print(f" Теплова енергія k_B T:      {res['kb_t_kev']:.3f} кЕв")
    print(f" Енергія піку Ґамова E₀:     {res['e0_numerical_kev']:.3f} кЕв")
    print(f" Ефективна ширина ΔE:        {res['delta_e_kev']:.3f} кЕв")
    print(f" Подавлення exp(-τ):         {math.exp(-res['tau']):.3e} (τ = {res['tau']:.2f})")
    print(f" Прозорість P(E₀):           {res['p_at_e0']:.3e}\n")


if __name__ == "__main__":
    # 1. Сонце: p + p реакція (T = 15.7 млн К)
    sim_pp = CoulombBarrierSimulator(z1=1, a1=1.0078, z2=1, a2=1.0078)
    print_simulation_report("Протон-протонний синтез (p + p)", sim_pp, 15.7e6)

    # 2. Термоядерний реактор ITER: d + t реакція (T = 100 млн К)
    sim_dt = CoulombBarrierSimulator(z1=1, a1=2.0141, z2=1, a2=3.0160)
    print_simulation_report("Дейтерій-тритієвий синтез (d + t)", sim_dt, 100.0e6)

    # 3. Безнейтронний синтез: p + 11B (T = 300 млн К)
    sim_pb = CoulombBarrierSimulator(z1=1, a1=1.0078, z2=5, a2=11.0093)
    print_simulation_report("Протон-борний синтез (p + ¹¹B)", sim_pb, 300.0e6)
