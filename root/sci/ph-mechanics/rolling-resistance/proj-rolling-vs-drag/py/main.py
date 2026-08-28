import math

G   = 9.81      # м/с², прискорення вільного падіння
RHO = 1.225     # кг/м³, повітря за 15 °C і 101.3 кПа


def crossover_speed(m, c_rr, cd_a, rho=RHO):
    """Швидкість (м/с), на якій опір повітря зрівнюється з опором коченню."""
    return math.sqrt(2.0 * c_rr * m * G / (rho * cd_a))


def aero_share(v, v_star):
    """Частка повітря в повному опорі на швидкості v (м/с)."""
    r = (v / v_star) ** 2          # F_повітря / F_кочення
    return r / (1.0 + r)


def crossover_speed_var(m, c0, c1, c2, cd_a, rho=RHO):
    """Те саме, але C_rr(v) = c0 + c1·v + c2·v² (форма моделі SAE J2452).
    None означає, що перетину немає взагалі: кочення дорожчає не повільніше."""
    a = 0.5 * rho * cd_a - c2 * m * G      # спільний коефіцієнт при v²
    if a <= 0.0:
        return None
    b = -c1 * m * G
    c = -c0 * m * G
    return (-b + math.sqrt(b * b - 4.0 * a * c)) / (2.0 * a)


def crossover_speed_num(m, c_rr_fn, cd_a, rho=RHO, v_hi=120.0):
    """Загальний випадок: C_rr задано довільною функцією швидкості.
    Ділимо відрізок навпіл за знаком різниці «повітря мінус кочення»."""
    def gap(v):
        return 0.5 * rho * cd_a * v * v - c_rr_fn(v) * m * G
    if gap(v_hi) <= 0.0:
        return None
    lo, hi = 0.0, v_hi                     # gap(0) < 0, gap(v_hi) > 0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if gap(mid) > 0.0:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def crossover_ground_speed(m, c_rr, cd_a, headwind=0.0, grade=0.0, rho=RHO):
    """Швидкість відносно ДОРОГИ з поправкою на зустрічний вітер і ухил."""
    theta = math.atan(grade)
    c_eff = c_rr * math.cos(theta) + math.sin(theta)
    return crossover_speed(m, c_eff, cd_a, rho) - headwind


def air_density(t_c, p_pa=101325.0):
    """ρ = p/(R·T), R = 287.05 Дж/(кг·К) для сухого повітря."""
    return p_pa / (287.05 * (t_c + 273.15))


FLEET = [
    # назва                   маса, кг   C_rr    C_d·A, м²
    ("велосипед із гонщиком",       85,  0.0040,  0.30),
    ("електросамокат",             100,  0.0150,  0.55),
    ("легковик-хетчбек",          1200,  0.0120,  0.66),
    ("електроседан",              1900,  0.0090,  0.53),
    ("фура, 40 т",               40000,  0.0060,  6.30),
]

for name, m, c_rr, cd_a in FLEET:
    v_star = crossover_speed(m, c_rr, cd_a)
    print("%-22s v* = %5.1f км/год   на 90 км/год повітря дає %4.1f %%"
          % (name, v_star * 3.6, 100.0 * aero_share(90 / 3.6, v_star)))

m, c_rr, cd_a = 1200, 0.012, 0.66
rho_cold = air_density(-10)
c_rr_v = lambda v: 0.0105 + 4.0e-6 * v * v      # v у м/с


def show(label, v_star):
    print("  %-28s %s" % (label, "—" if v_star is None
                          else "%5.1f км/год" % (v_star * 3.6)))


print()
print("той самий хетчбек, різні умови:")
show("рівна дорога, безвітря", crossover_speed(m, c_rr, cd_a))
show("зустрічний вітер 5 м/с", crossover_ground_speed(m, c_rr, cd_a, headwind=5.0))
show("підйом 3 %", crossover_ground_speed(m, c_rr, cd_a, grade=0.03))
show("мороз −10 °C (ρ = %.3f)" % rho_cold, crossover_speed(m, c_rr, cd_a, rho_cold))
show("C_rr = 0.0105 + 4e−6·v²", crossover_speed_var(m, 0.0105, 0.0, 4.0e-6, cd_a))
show("те саме половинним поділом", crossover_speed_num(m, c_rr_v, cd_a))
show("а якби c₂ = 4e−5", crossover_speed_var(m, 0.0105, 0.0, 4.0e-5, cd_a))
