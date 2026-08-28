import math
from typing import Optional, Tuple, List

def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """
    Розширений алгоритм Евкліда.
    Обчислює (d, x, y) такі, що a*x + b*y = d = НСД(a, b).
    Часова складність: O(log(min(|a|, |b|))).
    """
    if b == 0:
        if a < 0:
            return -a, -1, 0
        return a, 1, 0
    d, x1, y1 = extended_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return d, x, y

class LinearDiophantineSolver:
    """
    Аналізатор та розв'язник лінійного діофантового рівняння a*x + b*y = c.
    """
    
    def __init__(self, a: int, b: int, c: int):
        self.a = a
        self.b = b
        self.c = c
        self.d, self.x0, self.y0 = extended_gcd(abs(a), abs(b))
        
        # Коригуємо знаки для від'ємних коефіцієнтів
        if a < 0:
            self.x0 = -self.x0
        if b < 0:
            self.y0 = -self.y0

    def is_solvable(self) -> bool:
        """Перевіряє умова розв'язності: НСД(a, b) ділить c."""
        if self.a == 0 and self.b == 0:
            return self.c == 0
        return self.c % self.d == 0

    def particular_solution(self) -> Optional[Tuple[int, int]]:
        """
        Обчислює один частинний розв'язок (x1, y1).
        Повертає None, якщо цілих розв'язків не існує.
        """
        if not self.is_solvable():
            return None
        scale = self.c // self.d
        return self.x0 * scale, self.y0 * scale

    def non_negative_solutions(self) -> List[Tuple[int, int]]:
        """
        Знаходить усі невід'ємні розв'язки (x >= 0, y >= 0).
        """
        if not self.is_solvable():
            return []
        
        part = self.particular_solution()
        if part is None:
            return []
        x1, y1 = part
        
        step_x = self.b // self.d
        step_y = -self.a // self.d
        
        if step_x == 0 and step_y == 0:
            return [(x1, y1)] if x1 >= 0 and y1 >= 0 else []
        
        t_left = -float('inf')
        t_right = float('inf')
        
        if step_x > 0:
            t_left = max(t_left, math.ceil(-x1 / step_x))
        elif step_x < 0:
            t_right = min(t_right, math.floor(-x1 / step_x))

        if step_y > 0:
            t_left = max(t_left, math.ceil(-y1 / step_y))
        elif step_y < 0:
            t_right = min(t_right, math.floor(-y1 / step_y))

        if t_left > t_right or t_left == -float('inf') or t_right == float('inf'):
            return []
            
        sols = []
        for t in range(int(t_left), int(t_right) + 1):
            sols.append((x1 + step_x * t, y1 + step_y * t))
        return sols

def find_modular_obstruction(a: int, b: int, c: int, max_mod: int = 100) -> Optional[int]:
    """
    Аналізує наявність модульної перешкоди для рівняння a*x² + b*y² ≡ c (mod m).
    Повертає найменший модуль m ∈ [2, max_mod], за яким розв'язку не існує.
    """
    for m in range(2, max_mod + 1):
        squares = {(x * x) % m for x in range(m)}
        possible_lhs = {(a * sq1 + b * sq2) % m for sq1 in squares for sq2 in squares}
        if (c % m) not in possible_lhs:
            return m
    return None

if __name__ == "__main__":
    print("=== Тестування лінійного розв'язника ===")
    solver = LinearDiophantineSolver(5, 8, 43)
    print("Рівняння 5x + 8y = 43")
    print("Чи є розв'язки?", solver.is_solvable())
    print("Частинний розв'язок:", solver.particular_solution())
    print("Невід'ємні розв'язки (x >= 0, y >= 0):", solver.non_negative_solutions())

    print("\n=== Тестування детектора модульних перешкод ===")
    eq_tests = [(1, -3, 2), (1, 1, 7), (1, 1, 3)]
    for ca, cb, cc in eq_tests:
        m_obs = find_modular_obstruction(ca, cb, cc)
        if m_obs:
            print(f"Рівняння {ca}x² + ({cb})y² = {cc} має модульну перешкоду за mod {m_obs}")
        else:
            print(f"Рівняння {ca}x² + ({cb})y² = {cc} не має модульних перешкод до mod 100")
