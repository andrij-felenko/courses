import math

# Константи
R_GAS = 8.314462618  # Дж / (моль·К)
DULONG_PETIT_LIMIT = 3.0 * R_GAS  # ~24.94 Дж / (моль·К)

def heat_capacity_dulong_petit() -> float:
    """Класична теплоємність за законами Дюлонга — Пті."""
    return DULONG_PETIT_LIMIT

def heat_capacity_einstein(t_rel: float) -> float:
    """Теплоємність за моделлю Ейнштейна від безрозмірної температури T/Theta_E."""
    if t_rel <= 0:
        return 0.0
    x = 1.0 / t_rel
    if x > 80.0:
        return 0.0  # Експоненціальне виморожування
    
    exp_x = math.exp(x)
    factor = (x**2 * exp_x) / ((exp_x - 1.0)**2)
    return DULONG_PETIT_LIMIT * factor

def debye_integrand(x: float) -> float:
    """Підінтегральна функція Дебая: (x^4 * e^x) / (e^x - 1)^2."""
    if x <= 1e-7 or x > 80.0:
        return 0.0
    exp_x = math.exp(x)
    return (x**4 * exp_x) / ((exp_x - 1.0)**2)

def simpson_integrate(func, a: float, b: float, steps: int = 200) -> float:
    """Чисельне інтегрування методом Сімпсона."""
    if steps % 2 != 0:
        steps += 1
    h = (b - a) / steps
    total = func(a) + func(b)
    
    for i in range(1, steps, 2):
        total += 4.0 * func(a + i * h)
    for i in range(2, steps - 1, 2):
        total += 2.0 * func(a + i * h)
        
    return (h / 3.0) * total

def heat_capacity_debye(t_rel: float) -> float:
    """Теплоємність за моделлю Дебая від безрозмірної температури T/Theta_D."""
    if t_rel <= 0:
        return 0.0
    
    # Використання асимптотики T^3 для мальних T/Theta
    if t_rel < 0.08:
        factor = (12.0 * (math.pi**4) / 5.0) * (t_rel**3)
        return R_GAS * factor
        
    x_upper = 1.0 / t_rel
    integral_val = simpson_integrate(debye_integrand, 0.0, x_upper, steps=200)
    factor = 3.0 * (t_rel**3) * integral_val
    return DULONG_PETIT_LIMIT * factor

def run_simulation():
    """Виконання порівняльного розрахунку та друк таблиці."""
    temps = [0.02, 0.05, 0.10, 0.20, 0.30, 0.50, 0.70, 1.00, 1.50]
    
    print("=" * 72)
    print(" T / Theta | Dulong-Petit (J/mol/K) | Einstein (J/mol/K) | Debye (J/mol/K)")
    print("=" * 72)
    
    for t_rel in temps:
        cv_dp = heat_capacity_dulong_petit()
        cv_e = heat_capacity_einstein(t_rel)
        cv_d = heat_capacity_debye(t_rel)
        print(f"   {t_rel:5.2f}   |       {cv_dp:7.4f}          |      {cv_e:7.4f}       |    {cv_d:7.4f}")
        
    print("=" * 72)

if __name__ == "__main__":
    run_simulation()
