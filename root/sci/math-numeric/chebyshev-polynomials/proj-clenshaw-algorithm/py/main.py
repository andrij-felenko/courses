import math

def chebyshev_nodes(n):
    """Генерує n вузлів Чебишова (коренів T_n) на відрізку [-1, 1]."""
    nodes = []
    for k in range(1, n + 1):
        x_k = math.cos((2 * k - 1) * math.pi / (2 * n))
        nodes.append(x_k)
    return nodes

def fit_chebyshev_series(func, n):
    """Обчислює коефіцієнти c_m серії Чебишова степеня n-1 для функції func."""
    nodes = chebyshev_nodes(n)
    f_vals = [func(x) for x in nodes]
    
    coeffs = []
    for m in range(n):
        s = 0.0
        for k in range(n):
            # T_m(x_k) = cos(m * (2k+1) * pi / (2n))
            t_mk = math.cos(m * (2 * k + 1) * math.pi / (2 * n))
            s += f_vals[k] * t_mk
        c_m = (2.0 / n) * s
        coeffs.append(c_m)
    return coeffs

def clenshaw_eval(coeffs, x):
    """Обчислює значення суми (c_0 / 2) + sum_{k=1}^{N-1} c_k * T_k(x) у точці x."""
    n = len(coeffs)
    if n == 0:
        return 0.0
    if n == 1:
        return coeffs[0] / 2.0
    
    b_k1 = 0.0  # b_{k+1}
    b_k2 = 0.0  # b_{k+2}
    
    # Звороний хід від N-1 до 1
    for k in range(n - 1, 0, -1):
        b_k = 2.0 * x * b_k1 - b_k2 + coeffs[k]
        b_k2 = b_k1
        b_k1 = b_k
        
    return x * b_k1 - b_k2 + 0.5 * coeffs[0]

# Тестування на функції Рунге: g(x) = 1 / (1 + 25*x^2)
if __name__ == "__main__":
    def runge_function(x):
        return 1.0 / (1.0 + 25.0 * x * x)

    N = 11  # 11 вузлів
    coeffs = fit_chebyshev_series(runge_function, N)
    
    test_points = [-0.95, -0.5, 0.0, 0.5, 0.95]
    print(f"{'x':>8} | {'Точне значення':>15} | {'Інтерполяція':>15} | {'Похибка':>12}")
    print("-" * 58)
    for pt in test_points:
        exact = runge_function(pt)
        approx = clenshaw_eval(coeffs, pt)
        err = abs(exact - approx)
        print(f"{pt:8.2f} | {exact:15.8f} | {approx:15.8f} | {err:12.4e}")
