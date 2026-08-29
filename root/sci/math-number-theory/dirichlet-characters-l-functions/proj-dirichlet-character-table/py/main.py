import cmath
import math
import sys
from typing import List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


class DirichletCharacterTable:
    """Таблиця характерів Діріхле для циклічної групи залишків (ℤ/qℤ)*."""

    def __init__(self, q: int):
        self.q = q
        self.coprimes: List[int] = [x for x in range(1, q) if math.gcd(x, q) == 1]
        self.phi: int = len(self.coprimes)
        self.g: Optional[int] = self._find_primitive_root()
        self.discrete_log = {}
        self.table: List[List[complex]] = self._build_table()

    def _power_mod(self, base: int, exp: int, mod: int) -> int:
        return pow(base, exp, mod)

    def _find_primitive_root(self) -> Optional[int]:
        if self.q == 2:
            return 1
        phi_val = self.phi
        for g in range(2, self.q):
            if math.gcd(g, self.q) != 1:
                continue
            ok = True
            temp = phi_val
            p = 2
            while p * p <= temp:
                if temp % p == 0:
                    if self._power_mod(g, phi_val // p, self.q) == 1:
                        ok = False
                        break
                    while temp % p == 0:
                        temp //= p
                p += 1
            if temp > 1 and ok:
                if self._power_mod(g, phi_val // temp, self.q) == 1:
                    ok = False
            if ok:
                return g
        return None

    def _build_table(self) -> List[List[complex]]:
        if not self.g:
            raise ValueError(f"Модуль q={self.q} не має єдиного первісного кореня.")

        curr = 1
        for exp in range(self.phi):
            self.discrete_log[curr] = exp
            curr = (curr * self.g) % self.q

        table = []
        for k in range(self.phi):
            row = []
            for n in self.coprimes:
                idx = self.discrete_log[n]
                angle = 2.0 * math.pi * k * idx / self.phi
                val = cmath.rect(1.0, angle)
                row.append(val)
            table.append(row)
        return table

    def eval(self, char_idx: int, n: int) -> complex:
        """Обчислення значення χ(n) для довільного цілого числа n."""
        rem = n % self.q
        if math.gcd(rem, self.q) != 1:
            return 0.0 + 0.0j
        elem_idx = self.coprimes.index(rem)
        return self.table[char_idx][elem_idx]

    def compute_conductor(self, char_idx: int) -> int:
        """Пошук найменшого модуля-провідника d | q для даного характеру."""
        row = self.table[char_idx]
        for d in range(1, self.q + 1):
            if self.q % d != 0:
                continue
            is_cond = True
            for i, n in enumerate(self.coprimes):
                if n % d == 1 % d:
                    if abs(row[i] - 1.0) > 1e-6:
                        is_cond = False
                        break
            if is_cond:
                return d
        return self.q

    def is_even(self, char_idx: int) -> bool:
        """Перевірка парності характеру: χ(-1) = 1 (парний) або -1 (непарний)."""
        val = self.eval(char_idx, self.q - 1)
        return val.real > 0.0

    def is_real(self, char_idx: int) -> bool:
        """Перевірка, чи є характер дійсним (знаковим, порядок 1 або 2)."""
        return all(abs(z.imag) < 1e-6 for z in self.table[char_idx])

    def row_scalar_product(self, char_a: int, char_b: int) -> complex:
        """Скалярний добуток двох характерів (перше співвідношення ортогональності)."""
        return sum(
            self.table[char_a][i] * self.table[char_b][i].conjugate()
            for i in range(self.phi)
        )

    def col_scalar_product(self, elem_m: int, elem_n: int) -> complex:
        """Сума добутків усіх характерів (друге співвідношення ортогональності)."""
        return sum(
            self.eval(k, elem_m) * self.eval(k, elem_n).conjugate()
            for k in range(self.phi)
        )

    def fourier_delta_filter(self, a: int, n: int) -> complex:
        """Спектральне відновлення дельта-функції класу залишків δ(n ≡ a mod q)."""
        sum_val = sum(
            self.eval(k, a).conjugate() * self.eval(k, n)
            for k in range(self.phi)
        )
        return sum_val / self.phi

    def verify_orthogonality(self) -> Tuple[bool, bool]:
        """Повна чисельна перевірка обох співвідношень ортогональності."""
        row_ok = True
        for a in range(self.phi):
            for b in range(self.phi):
                dot = self.row_scalar_product(a, b)
                expected = self.phi if a == b else 0.0
                if abs(dot - expected) > 1e-5:
                    row_ok = False

        col_ok = True
        for m in self.coprimes:
            for n in self.coprimes:
                dot = self.col_scalar_product(m, n)
                expected = self.phi if m == n else 0.0
                if abs(dot - expected) > 1e-5:
                    col_ok = False

        return row_ok, col_ok

    def print_summary(self):
        """Виведення форматованої таблиці характерів та їхніх властивостей."""
        print(f"Таблиця характерів Діріхле (mod {self.q}), φ(q) = {self.phi}:")
        print("-" * 70)
        for k in range(self.phi):
            cond = self.compute_conductor(k)
            is_prim = "первісний" if cond == self.q else "індукований"
            is_ev = "парний" if self.is_even(k) else "непарний"
            is_re = "дійсний" if self.is_real(k) else "комплексний"

            print(f"χ_{k} [cond={cond}, {is_prim}, {is_ev}, {is_re}]:")
            vals = [
                f"n={n}:({z.real:+.2f}{z.imag:+.2f}i)"
                for n, z in zip(self.coprimes, self.table[k])
            ]
            print("  " + " ".join(vals))


if __name__ == "__main__":
    table = DirichletCharacterTable(5)
    table.print_summary()

    row_ok, col_ok = table.verify_orthogonality()
    print("\n--- Результати перевірки ортогональності ---")
    print(f"1. Ортогональність за рядками:    {'ПІДТВЕРДЖЕНО' if row_ok else 'ПОМИЛКА'}")
    print(f"2. Ортогональність за стовпчиками: {'ПІДТВЕРДЖЕНО' if col_ok else 'ПОМИЛКА'}")

    print("\n--- Спектральне відновлення дельта-фільтра δ(n ≡ 3 mod 5) ---")
    for n in table.coprimes:
        delta = table.fourier_delta_filter(3, n)
        print(f"δ({n} ≡ 3 mod 5) = {delta.real:.2f}")

