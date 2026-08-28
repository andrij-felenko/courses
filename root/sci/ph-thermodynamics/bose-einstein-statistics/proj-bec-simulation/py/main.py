# -*- coding: utf-8 -*-
"""
Чисельне моделювання бозе-конденсації ідеального та взаємодіючого газу,
розрахунок термодинамічних параметрів та просторових профілів густини.
"""

import math


def bose_polylog_3_2(z, terms=300):
    """
    Обчислення полілогарифма g_{3/2}(z) = sum_{k=1}^inf z^k / k^{1.5}
    для 0 <= z <= 1.
    """
    if z <= 0.0:
        return 0.0
    if z > 1.0:
        z = 1.0
    
    val = 0.0
    for k in range(1, terms + 1):
        term = (z ** k) / (k ** 1.5)
        val += term
        if term < 1e-12:
            break
    return val


def bose_polylog_5_2(z, terms=300):
    """
    Обчислення полілогарифма g_{5/2}(z) = sum_{k=1}^inf z^k / k^{2.5}
    для 0 <= z <= 1.
    """
    if z <= 0.0:
        return 0.0
    if z > 1.0:
        z = 1.0
    
    val = 0.0
    for k in range(1, terms + 1):
        term = (z ** k) / (k ** 2.5)
        val += term
        if term < 1e-12:
            break
    return val


# Константи дзета-функції Рімана
ZETA_3_2 = bose_polylog_3_2(1.0)  # ≈ 2.612375
ZETA_5_2 = bose_polylog_5_2(1.0)  # ≈ 1.341487


def solve_chemical_potential(t_rel, tol=1e-9):
    """
    Розв'язання рівняння n_th(T, mu) = N для T > T_c (t_rel > 1.0).
    Повертає безрозмірний хімічний потенціал alpha = -mu / (k_B * T) >= 0.
    """
    if t_rel <= 1.0:
        return 0.0  # При T <= T_c хімічний потенціал mu = 0 (alpha = 0)
    
    # Цільове значення фугітивності z = exp(-alpha): g_{3/2}(z) = ZETA_3_2 / (t_rel^1.5)
    target_g = ZETA_3_2 / (t_rel ** 1.5)
    
    z_low = 1e-15
    z_high = 1.0 - 1e-15
    
    # Метод бісекції для знаходження z
    for _ in range(100):
        z_mid = 0.5 * (z_low + z_high)
        g_mid = bose_polylog_3_2(z_mid)
        
        if abs(g_mid - target_g) < tol:
            break
        
        if g_mid < target_g:
            z_low = z_mid
        else:
            z_high = z_mid
            
    z_sol = 0.5 * (z_low + z_high)
    alpha_sol = -math.log(z_sol)
    return alpha_sol


def compute_bec_properties(t_rel_list):
    """
    Розрахунок комплексу термодинамічних параметрів бозе-газу
    для списку відносних температур T / T_c.
    """
    results = []
    
    for t_rel in t_rel_list:
        if t_rel <= 0.0:
            continue
            
        if t_rel <= 1.0:
            # Область існування бозе-конденсату (T <= T_c)
            n0_ratio = 1.0 - (t_rel ** 1.5)
            nth_ratio = t_rel ** 1.5
            alpha = 0.0
            z = 1.0
            # Теплоємність C_V / (N k_B) = 1.925 * (T / T_c)^1.5
            cv_ratio = (15.0 / 4.0) * (ZETA_5_2 / ZETA_3_2) * (t_rel ** 1.5)
        else:
            # Область вище критичної температури (T > T_c)
            n0_ratio = 0.0
            nth_ratio = 1.0
            alpha = solve_chemical_potential(t_rel)
            z = math.exp(-alpha)
            
            g32 = bose_polylog_3_2(z)
            g52 = bose_polylog_5_2(z)
            
            # Теплоємність у класичній/виродженій фазі
            cv_ratio = (15.0 / 4.0) * (g52 / g32) - 0.5 * alpha
            
        mu_rel = -alpha * t_rel  # mu / (k_B * T_c)
        
        results.append({
            't_rel': t_rel,
            'n0_ratio': n0_ratio,
            'nth_ratio': nth_ratio,
            'mu_rel': mu_rel,
            'z': z,
            'cv_ratio': cv_ratio
        })
        
    return results


def simulate_thomas_fermi_profile(num_points=10):
    """
    Розрахунок одномірного зрізу густини конденсату n_0(r)
    у наближенні Томаса — Фермі для гармонічної пастки.
    """
    r_max = 1.0  # У нормованих одиницях радіуса Томаса-Фермі R_TF
    profile = []
    
    for i in range(num_points + 1):
        r_norm = (i / float(num_points)) * r_max
        # n_0(r) / n_0(0) = 1 - (r / R_TF)^2
        density_norm = max(0.0, 1.0 - (r_norm ** 2))
        profile.append((r_norm, density_norm))
        
    return profile


def main():
    print("=== Чисельне моделювання термодинаміки ідеального бозе-газу ===")
    print(f"Константа ζ(3/2) = {ZETA_3_2:.6f}")
    print(f"Константа ζ(5/2) = {ZETA_5_2:.6f}\n")
    
    # Сітка відносних температур T / T_c
    temperatures = [0.2, 0.4, 0.6, 0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.3, 1.5, 2.0]
    data = compute_bec_properties(temperatures)
    
    print(f"{'T/T_c':^8} | {'N0/N':^8} | {'Nth/N':^8} | {'μ/(kB Tc)':^12} | {'Фугітивність z':^14} | {'C_V/(N kB)':^12}")
    print("-" * 75)
    
    for r in data:
        print(f"{r['t_rel']:8.2f} | {r['n0_ratio']:8.4f} | {r['nth_ratio']:8.4f} | {r['mu_rel']:12.4f} | {r['z']:14.6f} | {r['cv_ratio']:12.4f}")
        
    print("\n=== Профіль Томаса — Фермі густини бозе-конденсату n_0(r)/n_0(0) ===")
    tf_data = simulate_thomas_fermi_profile(8)
    for r_norm, n_norm in tf_data:
        bar = "█" * int(n_norm * 25)
        print(f"r/R_TF = {r_norm:4.2f} | n_0/n_max = {n_norm:5.3f} | {bar}")

    print("\nФізичні висновки чисельного розрахунку:")
    print("1. При T <= T_c хімічний потенціал фіксований на рівні mu = 0 (z = 1).")
    print("2. При T > T_c частка конденсату N0/N дорівнює 0, а хімічний потенціал стає від'ємним.")
    print("3. Максимум теплоємності досягається при T = T_c і становить C_V/(N kB) ≈ 1.925.")


if __name__ == "__main__":
    main()
