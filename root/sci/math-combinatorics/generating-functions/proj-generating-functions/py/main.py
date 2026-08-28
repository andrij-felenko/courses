# -*- coding: utf-8 -*-
"""Модуль обчислення формальних степеневі рядів (Formal Power Series) мовою Python."""

class FormalPowerSeries:
    def __init__(self, coeffs, degree=16):
        """Ініціалізація ряду вектором коефіцієнтів із відтинанням до степеня degree."""
        self.deg = degree
        # Заповнюємо або усікаємо масив коефіцієнтів до довжини degree
        self.c = [float(x) for x in coeffs[:degree]]
        if len(self.c) < degree:
            self.c.extend([0.0] * (degree - len(self.c)))

    def __add__(self, other):
        """Почленне додавання двох рядів: C(x) = A(x) + B(x)."""
        res = [self.c[i] + other.c[i] for i in range(self.deg)]
        return FormalPowerSeries(res, self.deg)

    def __sub__(self, other):
        """Почленне віднімання двох рядів: C(x) = A(x) - B(x)."""
        res = [self.c[i] - other.c[i] for i in range(self.deg)]
        return FormalPowerSeries(res, self.deg)

    def __mul__(self, other):
        """Дискретна згортка (множення рядів): C(x) = A(x) * B(x) mod x^N."""
        res = [0.0] * self.deg
        for i in range(self.deg):
            for j in range(self.deg - i):
                res[i + j] += self.c[i] * other.c[j]
        return FormalPowerSeries(res, self.deg)

    def invert(self):
        """Алгебраїчне обернення ряду 1 / A(x). Вимагає A[0] != 0."""
        if abs(self.c[0]) < 1e-12:
            raise ValueError("Вільний член A[0] дорівнює 0, обернений ряд не існує.")
        
        b = [0.0] * self.deg
        b[0] = 1.0 / self.c[0]
        
        for k in range(1, self.deg):
            acc = 0.0
            for i in range(1, k + 1):
                acc += self.c[i] * b[k - i]
            b[k] = -acc / self.c[0]
            
        return FormalPowerSeries(b, self.deg)

    def derivative(self):
        """Формальне диференціювання: A'(x) = sum(n * a_n * x^(n-1))."""
        res = [0.0] * self.deg
        for i in range(1, self.deg):
            res[i - 1] = float(i) * self.c[i]
        return FormalPowerSeries(res, self.deg)


def solve_fibonacci(degree=12):
    """Обчислення чисел Фібоначчі за допомогою твірної функції F(x) = x / (1 - x - x^2)."""
    # Знаменник Q(x) = 1 - x - x^2
    q_coeffs = [1.0, -1.0, -1.0]
    Q = FormalPowerSeries(q_coeffs, degree)
    
    # Знаходимо 1 / Q(x)
    Q_inv = Q.invert()
    
    # Чисельник P(x) = x
    P = FormalPowerSeries([0.0, 1.0], degree)
    
    # F(x) = P(x) * (1 / Q(x))
    F = P * Q_inv
    return [round(x) for x in F.c]


def solve_catalan(degree=10):
    """Обчислення чисел Каталана через ітерацію C(x) = 1 + x * C(x)^2."""
    # Починаємо з наближення C_0(x) = 1
    C = FormalPowerSeries([1.0], degree)
    
    # Застосовуємо ітерацію фіксованої точки N разів
    for _ in range(degree):
        # C_{k+1}(x) = 1 + x * C_k(x)^2
        C_sq = C * C
        # Множення на x відповідає зсуву коефіцієнтів праворуч
        x_C_sq_coeffs = [0.0] + C_sq.c[:-1]
        x_C_sq = FormalPowerSeries(x_C_sq_coeffs, degree)
        
        one = FormalPowerSeries([1.0], degree)
        C = one + x_C_sq
        
    return [round(x) for x in C.c]


if __name__ == "__main__":
    print("Числа Фібоначчі через твірну функцію x/(1-x-x^2):")
    fibs = solve_fibonacci(12)
    for n, val in enumerate(fibs):
        print(f"F[{n}] = {val}")

    print("\nЧисла Каталана через твірну функцію C(x) = 1 + x*C(x)^2:")
    cats = solve_catalan(8)
    for n, val in enumerate(cats):
        print(f"C[{n}] = {val}")
