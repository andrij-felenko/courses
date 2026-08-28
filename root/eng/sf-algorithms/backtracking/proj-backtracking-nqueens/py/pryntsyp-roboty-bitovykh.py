import time

class NQueensBitmask:
    def __init__(self, n: int):
        self.n = n
        # limit створює маску з n одиниць у молодших бітах
        self.limit = (1 << n) - 1
        self.solution_count = 0

    def _solve(self, cols: int, diag1: int, diag2: int) -> None:
        # Усі стовпчики заповнені — знайдено повний розв'язок
        if cols == self.limit:
            self.solution_count += 1
            return

        # Знаходимо маску безпечних позицій для поточного рядка
        pos = self.limit & ~(cols | diag1 | diag2)

        while pos > 0:
            # Магічна побітова операція: витягуємо наймолодший 1-біт
            bit = pos & -pos
            # Скидаємо цей біт з доступних
            pos -= bit

            # Рекурсивне дослідження наступного рядка
            # diag1 зміщується вліво, diag2 — вправо
            self._solve(cols | bit, (diag1 | bit) << 1, (diag2 | bit) >> 1)

    def count_solutions(self) -> int:
        self.solution_count = 0
        self._solve(0, 0, 0)
        return self.solution_count

if __name__ == "__main__":
    n = 12
    solver = NQueensBitmask(n)
    
    t0 = time.perf_counter()
    solutions = solver.count_solutions()
    t1 = time.perf_counter()

    print(f"Кількість розв'язків для {n}-Ферзів: {solutions}")
    print(f"Час виконання: {(t1 - t0) * 1000:.2f} мс")
