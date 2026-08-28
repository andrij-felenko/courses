import cmath
import math

class DirichletCharacterTable:
    def __init__(self, q: int):
        self.q = q
        self.coprimes = [x for x in range(1, q) if math.gcd(x, q) == 1]
        self.phi = len(self.coprimes)
        self.g = self._find_primitive_root()
        self.table = self._build_table()

    def _power_mod(self, base: int, exp: int, mod: int) -> int:
        return pow(base, exp, mod)

    def _find_primitive_root(self):
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

    def _build_table(self):
        if not self.g:
            raise ValueError(f"Модуль q={self.q} не має єдиного первісного кореня.")
        discrete_log = {}
        curr = 1
        for exp in range(self.phi):
            discrete_log[curr] = exp
            curr = (curr * self.g) % self.q

        table = []
        for k in range(self.phi):
            row = []
            for n in self.coprimes:
                idx = discrete_log[n]
                angle = 2 * math.pi * k * idx / self.phi
                val = cmath.rect(1.0, angle)
                row.append(val)
            table.append(row)
        return table

    def compute_conductor(self, char_idx: int) -> int:
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

    def verify_orthogonality(self):
        print(f"\n--- Перевірка першої ортогональності (mod {self.q}) ---")
        for a in range(self.phi):
            for b in range(self.phi):
                dot = sum(self.table[a][i] * self.table[b][i].conjugate() for i in range(self.phi))
                expected = self.phi if a == b else 0
                assert abs(dot - expected) < 1e-5
        print("Перше співвідношення ортогональності підтверджено!")


if __name__ == "__main__":
    t = DirichletCharacterTable(5)
    for k in range(t.phi):
        d = t.compute_conductor(k)
        kind = "первісний" if d == t.q else "індукований"
        vals = [f"{z.real:.2f}+{z.imag:.2f}j" for z in t.table[k]]
        print(f"χ_{k} [d={d}, {kind}]: {vals}")
    t.verify_orthogonality()
