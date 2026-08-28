import numpy as np

def virasoro_cocycle(n: int, m: int, c: float) -> float:
    """Обчислює центральний член коциклу алгебри Вірасоро: (c / 12) * (n^3 - n) * delta_{n+m, 0}."""
    if n + m == 0:
        return (c / 12.0) * (n**3 - n)
    return 0.0

def verify_jacobi_identity(k: int, m: int, n: int, c: float) -> float:
    """Перевіряє тотожність Якобі для трійки генераторів (L_k, L_m, L_n).
    Повертає суму центральних внесків (має бути 0)."""
    # [L_k, [L_m, L_n]] -> (m - n)*g(k, m+n)
    term1 = (m - n) * virasoro_cocycle(k, m + n, c)
    # [L_m, [L_n, L_k]] -> (n - k)*g(m, n+k)
    term2 = (n - k) * virasoro_cocycle(m, n + k, c)
    # [L_n, [L_k, L_m]] -> (k - m)*g(n, k+m)
    term3 = (k - m) * virasoro_cocycle(n, k + m, c)
    
    return term1 + term2 + term3

def kac_determinant_level2(c: float, h: float) -> float:
    """Обчислює визначник Каца на рівні N = 2 у базисі {|1> = L_{-2}|h>, |2> = L_{-1}^2|h>}.
    
    Матриця Грама M^{(2)} має елементи M_ij = <h| (L_i)^+ L_j |h>:
    M_11 = <h| L_2 L_{-2} |h> = 4h + c/2
    M_12 = <h| L_2 L_{-1}^2 |h> = 6h
    M_21 = <h| (L_1)^2 L_{-2} |h> = 6h
    M_22 = <h| (L_1)^2 L_{-1}^2 |h> = 4h(2h + 1)
    """
    m11 = 4.0 * h + c / 2.0
    m12 = 6.0 * h
    m21 = 6.0 * h
    m22 = 4.0 * h * (2.0 * h + 1.0)
    
    gram_matrix = np.array([[m11, m12], [m21, m22]], dtype=np.float64)
    det_val = np.linalg.det(gram_matrix)
    
    # Теоретична формула Каца: det M^{(2)}(c, h) = 2 * h * (16 * h^2 + 2 * c * h - 10 * h + c)
    theory_val = 2.0 * h * (16.0 * h**2 + 2.0 * c * h - 10.0 * h + c)
    
    print(f"Обчислена матриця Грама M^(2):\n{gram_matrix}")
    print(f"Чисельний det M^(2): {det_val:.6f}")
    print(f"Аналітична формула Каца: {theory_val:.6f}")
    return det_val

if __name__ == "__main__":
    c_val, h_val = 0.5, 1.0 / 16.0  # Параметри критичної моделі Ізинга (сигма-поле)
    print("--- Перевірка тотожності Якобі ---")
    res_jacobi = verify_jacobi_identity(2, -5, 3, c=26.0)
    print(f"Якобі-помилка для (2, -5, 3): {res_jacobi:.12f}")
    
    print("\n--- Визначник Каца для рівню N = 2 ---")
    kac_determinant_level2(c_val, h_val)
