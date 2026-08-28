class GaloisField:
    """Універсальна програмна модель скінченного поля GF(2^n)."""
    def __init__(self, poly: int, bits: int):
        self.poly = poly
        self.bits = bits
        self.order = 1 << bits
        self.exp = [0] * self.order
        self.log = [0] * self.order
        self._build_tables()

    def _build_tables(self):
        val = 1
        for i in range(self.order - 1):
            self.exp[i] = val
            self.log[val] = i
            # xtime редукція
            val <<= 1
            if val & self.order:
                val ^= self.poly
        self.exp[self.order - 1] = 1

    def add(self, a: int, b: int) -> int:
        return a ^ b

    def mul(self, a: int, b: int) -> int:
        if a == 0 or b == 0:
            return 0
        idx = (self.log[a] + self.log[b]) % (self.order - 1)
        return self.exp[idx]

    def inv(self, a: int) -> int:
        if a == 0:
            return 0
        idx = (self.order - 1 - self.log[a]) % (self.order - 1)
        return self.exp[idx]


def aes_sbox(b: int) -> int:
    """Обчислення байта AES S-Box: мультиплікативне обернення + афінний зсув."""
    gf = GaloisField(0x11B, 8)
    inv = gf.inv(b)
    s = inv
    s ^= ((inv << 1) | (inv >> 7)) & 0xFF
    s ^= ((inv << 2) | (inv >> 6)) & 0xFF
    s ^= ((inv << 3) | (inv >> 5)) & 0xFF
    s ^= ((inv << 4) | (inv >> 4)) & 0xFF
    return s ^ 0x63


# Тестування полів GF(2^3) та GF(2^8)
if __name__ == "__main__":
    gf8 = GaloisField(poly=0x0B, bits=3)
    res_8 = gf8.mul(5, 3)
    print(f"GF(2^3) Python: 5 * 3 = {res_8} (очікується 4)")

    gf256 = GaloisField(poly=0x11B, bits=8)
    a, b = 0x57, 0x83
    res_256 = gf256.mul(a, b)
    print(f"GF(2^8) Python: 0x{a:02X} * 0x{b:02X} = 0x{res_256:02X} (очікується 0xC1)")

    inv_a = gf256.inv(a)
    check = gf256.mul(a, inv_a)
    print(f"GF(2^8) Python: 0x{a:02X}^(-1) = 0x{inv_a:02X}, перевірка: {check}")

    print(f"AES S-Box Python: S(0x53) = 0x{aes_sbox(0x53):02X} (очікується 0xED)")
