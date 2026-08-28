import math
from dataclasses import dataclass

# Фізичні константи
K_B_EV = 8.617333e-5   # Постійна Больцмана, еВ/К
Q_ELEC = 1.602176e-19  # Заряд електрона, Кл

@dataclass
class SRHTrapParams:
    et_minus_ei_ev: float  # E_t - E_i в еВ
    tau_n0_s: float        # τ_n0 в секундах (1 / (C_n * N_t))
    tau_p0_s: float        # τ_p0 в секундах (1 / (C_p * N_t))

@dataclass
class SRHResult:
    r_srh: float           # Швидкість рекомбінації, см⁻³·с⁻¹
    tau_eff_s: float       # Ефективний час життя, с
    is_generation: bool    # True, якщо відбувається генерація (n*p < n_i²)

def compute_srh(params: SRHTrapParams, n: float, p: float, 
                temp_k: float = 300.0, n_i: float = 1.5e10) -> SRHResult:
    """Обчислює швидкість рекомбінації SRH та час життя для кремнію."""
    vt = K_B_EV * temp_k
    
    # Обчислення параметрів емісії n_1 та p_1
    exp_factor = math.exp(params.et_minus_ei_ev / vt)
    n_1 = n_i * exp_factor
    p_1 = n_i / exp_factor
    
    # Чисельник та знаменник формули SRH
    np_product = n * p
    ni_sq = n_i * n_i
    numerator = np_product - ni_sq
    
    denominator = params.tau_p0_s * (n + n_1) + params.tau_n0_s * (p + p_1)
    
    r_srh = numerator / denominator
    
    # Ефективний час життя відносно надлишкової концентрації
    # Розраховуємо для p-типу під низькою/високою інжекцією (n_0 << p_0)
    delta_n = max(n - (ni_sq / max(p, 1.0)), 1e-12)
    tau_eff = delta_n / r_srh if r_srh > 0 else float('inf')
    
    return SRHResult(
        r_srh=r_srh,
        tau_eff_s=tau_eff,
        is_generation=(numerator < 0)
    )

def main():
    # Приклад: пастка золота у кремнії p-типу (p0 = 1e16 см⁻³)
    trap = SRHTrapParams(et_minus_ei_ev=0.02, tau_n0_s=1e-6, tau_p0_s=1e-6)
    p0 = 1e16
    
    print("--- Симуляція залежності часу життя від інжекції Δn ---")
    for log_dn in range(10, 18):
        dn = 10.0 ** log_dn
        n = (1.5e10**2 / p0) + dn
        p = p0 + dn
        res = compute_srh(trap, n, p)
        print(f"Δn = {dn:.1e} см⁻³ | R_SRH = {res.r_srh:.2e} см⁻³с⁻¹ | τ_eff = {res.tau_eff_s*1e6:.3f} мкс")

if __name__ == "__main__":
    main()
