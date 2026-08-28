import math
from typing import Tuple

def baker_davenport_reduction(theta: float, beta: float, K: float, c: float, M: int) -> int:
    """Знижує початкову межу M для нерівності |b1*theta - b2 + beta| < K * exp(-c * B)

    Параметри:
      theta: ірраціональне число (напр. ln(α1)/ln(α2))
      beta:  зсув (напр. ln(μ)/ln(α2))
      K, c:  позитивні константи з теоретичної оцінки
      M:     початкова велетенська межа Бейкера (напр. 10^30)

    Повертає:
      Нову редуковану межу B_new << M
    """
    current_M = M
    step = 0

    while True:
        step += 1
        target_q = 6 * current_M
        
        # Обчислення підхідних дробів за допомогою алгоритму ланцюгових дробів
        x = theta
        p_n2, p_n1 = 1, math.floor(x)
        q_n2, q_n1 = 0, 1
        
        while q_n1 <= target_q:
            rem = x - math.floor(x)
            if abs(rem) < 1e-15:
                break
            x = 1.0 / rem
            an = math.floor(x)
            
            pn = an * p_n1 + p_n2
            qn = an * q_n1 + q_n2
            
            p_n2, p_n1 = p_n1, pn
            q_n2, q_n1 = q_n1, qn
        
        q_found = q_n1
        p_found = p_n1
        
        # Відстань q * beta до найближчого цілого
        q_beta = q_found * beta
        dist_to_int = abs(q_beta - round(q_beta))
        
        # Відхилення підхідного дробу |q * theta - p|
        delta_theta = abs(q_found * theta - p_found)
        
        epsilon = dist_to_int - current_M * delta_theta
        
        if epsilon <= 0:
            # Якщо epsilon <= 0, збільшуємо current_M для виходу з тупика
            current_M *= 2
            continue
            
        # Обчислення нової межі B_new
        b_new = math.floor(math.log(q_found * K / epsilon) / c)
        
        print(f"Крок {step}: q = {q_found}, ε = {epsilon:.6e} -> Нова межа B = {b_new}")
        
        if b_new >= current_M or b_new == current_M - 1:
            # Збіжність досягнута
            return current_M
        
        current_M = b_new
        if current_M <= 50:
            return current_M


def solve_thue_example():
    """Розв'язання чисельного прикладу рівняння Тюе за допомогою редукції"""
    print("=== Розв meння нерівності методом Бейкера — Давенпорта ===")
    theta_val = math.log(2) / math.log(3)
    beta_val = math.log(5) / math.log(3)
    K_val = 100.0
    c_val = 0.8
    M_start = 10**18

    final_bound = baker_davenport_reduction(theta_val, beta_val, K_val, c_val, M_start)
    print(f"\nОстаточна обчислювальна межа: B <= {final_bound}")


if __name__ == "__main__":
    solve_thue_example()
