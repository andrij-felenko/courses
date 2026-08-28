from math import sqrt

# оберти зависання з квадратичної моделі T = k_T·n²
T_max   = 8.0      # Н на повному газі
n_max   = 400.0    # об/с на повному газі
T_hover = 2.94     # Н на гвинт, щоб висіти

k_T   = T_max / (n_max * n_max)      # коефіцієнт тяги гвинта
n_hov = sqrt(T_hover / k_T)          # оберти зависання
throttle_hover = n_hov / n_max       # частка газу на завис

# n_hov ≈ 242 об/с  →  throttle_hover ≈ 0.61
