import math

# Коефіцієнти профілю як функції кута атаки (спрощена лінійна модель до зриву).
def cl_of_alpha(a_rad):
    cl = 2.0 * math.pi * a_rad          # тонке крило: C_L ≈ 2π·α
    return max(-1.4, min(1.4, cl))      # груба межа зриву

def cd_of_alpha(a_rad):
    return 0.02 + 0.05 * a_rad * a_rad  # паразитний + індукований опір

# Одна смужка лопаті на радіусі r: ітеративно узгодити елемент лопаті
# з теорією імпульсу й повернути внески в тягу (dT) і момент (dQ).
# V0 — швидкість польоту (м/с); omega — кутова швидкість (рад/с);
# r, dr, c — радіус, товщина смужки, хорда (м); beta — кут установки (рад);
# B — число лопатей; rho — густина повітря.
def blade_element(V0, omega, r, dr, c, beta, B, rho):
    a, ap = 0.0, 0.0                    # початкові індукції
    phi = W = 0.0
    sigma = B * c / (2.0 * math.pi * r) # місцева щільність лопаті

    for _ in range(100):
        # 2) кут потоку з поточних індукцій
        V_ax = V0 * (1.0 + a)
        V_tan = omega * r * (1.0 - ap)
        phi = math.atan2(V_ax, V_tan)
        W = math.hypot(V_ax, V_tan)

        # 3) кут атаки й коефіцієнти профілю
        alpha = beta - phi
        Cl = cl_of_alpha(alpha)
        Cd = cd_of_alpha(alpha)

        # 4) проєкції на вісь (нормальна) і на площину (тангенційна)
        Cn = Cl * math.cos(phi) - Cd * math.sin(phi)
        Ct = Cl * math.sin(phi) + Cd * math.cos(phi)

        # 5) нові індукції з рівнянь зшивання; f = a/(1+a) → a = f/(1−f)
        s = math.sin(phi)
        f_ax = sigma * Cn / (4.0 * s * s)
        f_tan = sigma * Ct / (4.0 * s * math.cos(phi))
        a_new = f_ax / (1.0 - f_ax)
        ap_new = f_tan / (1.0 + f_tan)

        # 6) перевірка збіжності
        if abs(a_new - a) < 1e-5 and abs(ap_new - ap) < 1e-5:
            a, ap = a_new, ap_new
            break
        a, ap = a_new, ap_new

    # сили смужки з усталеного трикутника швидкостей
    q = 0.5 * rho * W * W               # динамічний напір ½ρW²
    dL = q * c * cl_of_alpha(beta - phi) * dr
    dD = q * c * cd_of_alpha(beta - phi) * dr

    dT = B * (dL * math.cos(phi) - dD * math.sin(phi))     # тяга смужки (усі лопаті)
    dQ = B * (dL * math.sin(phi) + dD * math.cos(phi)) * r # момент смужки
    return dT, dQ
