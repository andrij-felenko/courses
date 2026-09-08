import math
from typing import List, Tuple

class GoelOkumotoMLE:
    def __init__(self, failure_times: List[float]):
        if not failure_times:
            raise ValueError("Масив часових міток відмов не може бути порожнім")
        self.times = sorted(failure_times)
        self.n = len(self.times)
        self.t_n = self.times[-1]
        self.t_mean = sum(self.times) / self.n

    def fit(self, tolerance: float = 1e-7, max_iterations: int = 100) -> Tuple[float, float, float]:
        # Перевірка умови існування кореня: t_mean < t_n / 2
        # Якщо відмови накопичуються ближче до кінця, модель сигналізує про прискорення (потрібна модель Ямади)
        if self.t_mean >= self.t_n / 2.0:
            raise ValueError(
                "Неможливо підігнати модель Гоела-Окумото: середній час відмов занадто близький до кінця. "
                "Дані свідчать про S-подібну динаміку."
            )

        # Початкове наближення для b
        b = 1.0 / (2.0 * self.t_mean)

        for _ in range(max_iterations):
            exp_btn = math.exp(b * self.t_n)
            denom = exp_btn - 1.0

            # Значення функції f(b)
            f_val = (1.0 / b) - self.t_mean - (self.t_n / denom)

            # Значення похідної f'(b)
            f_prime = (-1.0 / (b * b)) + ((self.t_n * self.t_n * exp_btn) / (denom * denom))

            delta = f_val / f_prime
            b_next = b - delta

            if abs(delta) < tolerance:
                b_opt = b_next
                break
            b = b_next
        else:
            b_opt = b

        # Розрахунок оцінки загального пулу a та залишкових дефектів
        a_opt = self.n / (1.0 - math.exp(-b_opt * self.t_n))
        residual_defects = a_opt - self.n

        return a_opt, b_opt, residual_defects
