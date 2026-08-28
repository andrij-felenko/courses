import math
import secrets

def extended_gcd(a: int, b: int):
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def mod_inverse(a: int, m: int) -> int:
    gcd, x, _ = extended_gcd(a, m)
    if gcd != 1:
        raise ValueError("Модульний інверс не існує")
    return (x % m + m) % m

def lcm(a: int, b: int) -> int:
    return (a * b) // math.gcd(a, b)

class PaillierPublicKey:
    def __init__(self, n: int):
        self.n = n
        self.n_sq = n * n
        self.g = n + 1  # Канонічний генератор

    def encrypt(self, m: int) -> int:
        if not (0 <= m < self.n):
            # Обробка від'ємних чисел через доповняльний код
            m = m % self.n

        # Вибір випадкового r з Z_n*
        while True:
            r = secrets.randbelow(self.n - 1) + 1
            if math.gcd(r, self.n) == 1:
                break

        # c = (1 + m*n) * r^n mod n^2
        c_msg = (1 + m * self.n) % self.n_sq
        c_rnd = pow(r, self.n, self.n_sq)
        return (c_msg * c_rnd) % self.n_sq

    def add(self, c1: int, c2: int) -> int:
        return (c1 * c2) % self.n_sq

    def mul_scalar(self, c: int, k: int) -> int:
        if k < 0:
            # Скалярне множення на від'ємне число через інверсію
            c = mod_inverse(c, self.n_sq)
            k = -k
        return pow(c, k, self.n_sq)

class PaillierPrivateKey:
    def __init__(self, p: int, q: int):
        self.n = p * q
        self.n_sq = self.n * self.n
        self.lam = lcm(p - 1, q - 1)
        self.pub = PaillierPublicKey(self.n)
        
        # μ = (L(g^λ mod n²))⁻¹ mod n = λ⁻¹ mod n (для g = 1 + n)
        self.mu = mod_inverse(self.lam, self.n)

    def decrypt(self, c: int) -> int:
        # u = c^λ mod n²
        u = pow(c, self.lam, self.n_sq)
        
        # L(u) = (u - 1) / n
        l_u = (u - 1) // self.n
        
        # m = L(u) * μ mod n
        m = (l_u * self.mu) % self.n
        
        # Декодування від'ємних чисел
        if m > self.n // 2:
            m -= self.n
        return m

# Демонстрація використання
if __name__ == "__main__":
    # Прості числа для демонстрації (у продакшені 1024+ біт кожне)
    p, q = 61, 53
    key = PaillierPrivateKey(p, q)
    pub = key.pub

    print(f"Модуль n = {pub.n}, n² = {pub.n_sq}")

    # Шифруємо три голоси громадянам: +1 (ЗА), -1 (ПРОТИ), +1 (ЗА)
    v1 = pub.encrypt(1)
    v2 = pub.encrypt(-1)
    v3 = pub.encrypt(1)

    # Сервер підсумовує зашифровані голоси
    total_c = pub.add(v1, v2)
    total_c = pub.add(total_c, v3)

    # Лічильна комісія розшифровує результат
    total_result = key.decrypt(total_c)
    print(f"Результат анонімного підрахунку: {total_result} (Очікувалося: 1)")
