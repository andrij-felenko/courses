# -*- coding: utf-8 -*-
"""Чисельний аналіз кругових відображень та теореми Данжуа (Python)."""
import math

class CircleMapAnalyzer:
    def __init__(self, omega: float, k_param: float):
        self.omega = omega
        self.k = k_param

    def lift(self, x: float) -> float:
        """Підйом F(x) синус-кругового відображення на R."""
        return x + self.omega - (self.k / (2.0 * math.pi)) * math.sin(2.0 * math.pi * x)

    def lift_prime(self, x: float) -> float:
        """Похідна підйому F'(x)."""
        return 1.0 - self.k * math.cos(2.0 * math.pi * x)

    def compute_rotation_number(self, n_iterations: int = 100000) -> float:
        """Обчислення числа обертання Пуанкаре rho(f)."""
        x = 0.0
        for _ in range(n_iterations):
            x = self.lift(x)
        return (x / n_iterations) % 1.0

    def compute_derivative_product(self, x0: float, q_steps: int) -> float:
        """Обчислення добутку похідних (f^{q_k}')(x0) вздовж орбіти."""
        prod = 1.0
        curr_x = x0
        for _ in range(q_steps):
            prod *= self.lift_prime(curr_x % 1.0)
            curr_x = self.lift(curr_x)
        return prod

def get_continued_fraction_convergents(alpha: float, max_depth: int = 10):
    """Обчислення знаменників q_k ланцюгового дробу для ірраціонального alpha."""
    convergents = []
    val = alpha
    p_prev, p_curr = 1, 0
    q_prev, q_curr = 0, 1

    for _ in range(max_depth):
        a = int(math.floor(val))
        p_next = a * p_curr + p_prev
        q_next = a * q_curr + q_prev

        convergents.append((p_next, q_next))
        p_prev = p_curr; p_curr = p_next
        q_prev = q_curr; q_curr = q_next

        rem = val - a
        if rem < 1e-12:
            break
        val = 1.0 / rem
    return convergents

def main():
    # Золотий перетин (ірраціональне число обертання)
    golden_ratio = (math.sqrt(5.0) - 1.0) / 2.0
    print(f"Цільове ірраціональне alpha = {golden_ratio:.8f}")

    # C^2 гладке синус-кругове відображення при K = 0.5 (субкритичний режим)
    analyzer = CircleMapAnalyzer(omega=golden_ratio, k_param=0.5)

    rho = analyzer.compute_rotation_number(100000)
    print(f"Обчислене число обертання rho(f) = {rho:.8f}")

    convergents = get_continued_fraction_convergents(rho, max_depth=8)
    print("\n--- Перевірка нерівності спотворення Данжуа ---")
    print("k | q_k   | log(f^{q_k}')(x1) | log(f^{q_k}')(x2) | Різниця (<= V)")
    print("-" * 65)

    x1, x2 = 0.1, 0.65
    for idx, (p, q) in enumerate(convergents[2:], start=2):
        d1 = analyzer.compute_derivative_product(x1, q)
        d2 = analyzer.compute_derivative_product(x2, q)
        log_d1 = math.log(abs(d1))
        log_d2 = math.log(abs(d2))
        diff = abs(log_d1 - log_d2)
        print(f"{idx} | {q:<5} | {log_d1:<17.6f} | {log_d2:<17.6f} | {diff:.6f}")

if __name__ == "__main__":
    main()
