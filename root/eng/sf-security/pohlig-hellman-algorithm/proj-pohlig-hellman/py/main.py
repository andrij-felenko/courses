import math
from typing import List, Tuple, Dict

def mod_pow(base: int, exp: int, mod: int) -> int:
    """Швидке модульне піднесення до степеня (base^exp mod mod)."""
    res = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:
            res = (res * base) % mod
        base = (base * base) % mod
        exp //= 2
    return res

def ext_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """
    Розширений алгоритм Евкліда.
    Повертає трійку (gcd, x, y), таку що a*x + b*y = gcd.
    """
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = ext_gcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return (g, x, y)

def mod_inv(a: int, mod: int) -> int:
    """Обчислення модульного оберненого елемента a^(-1) mod mod."""
    g, x, _ = ext_gcd(a, mod)
    if g != 1:
        raise ValueError(f"Число {a} не має оберненого за модулем {mod} (НСД = {g})")
    return (x % mod + mod) % mod

def solve_dlog_bsgs(g: int, h: int, p_order: int, mod: int) -> int:
    """
    Розв'язання дискретного логарифма g^x = h mod mod у підгрупі простого порядку p_order
    за алгоритмом Baby-Step Giant-Step (метод Шенкса).
    Часова складність: O(sqrt(p_order)), просторова складність: O(sqrt(p_order)).
    """
    m = math.isqrt(p_order) + 1
    table: Dict[int, int] = {}
    
    # Baby steps: попередній розрахунок g^j mod mod для 0 <= j < m
    cur = 1
    for j in range(m):
        if cur not in table:
            table[cur] = j
        cur = (cur * g) % mod
        
    # Giant steps: обчислення множника кроку gamma = g^(-m) mod mod
    g_m = mod_pow(g, m, mod)
    factor = mod_inv(g_m, mod)
    
    gamma = h % mod
    for i in range(m):
        if gamma in table:
            x = i * m + table[gamma]
            if x < p_order:
                return x
        gamma = (gamma * factor) % mod
        
    raise ValueError(f"Дискретний логарифм для h={h} не знайдено в підгрупі порядку {p_order}")

def solve_prime_power_subgroup(g: int, h: int, p: int, e: int, n: int, mod: int) -> int:
    """
    Знаходження x_i = x mod (p^e) для примарної підгрупи порядку p^e методом ліфтингу.
    g, h — генератор та ціль у вихідній групі, n — повний порядок групи.
    """
    p_e = p ** e
    # 1. Проекція генератора та цільового елемента на підгрупу порядку p^e
    proj_exp = n // p_e
    g_sub = mod_pow(g, proj_exp, mod)
    h_sub = mod_pow(h, proj_exp, mod)
    
    # 2. Базовий генератор підгрупи простого порядку p: gamma = g_sub^(p^(e-1))
    gamma = mod_pow(g_sub, p ** (e - 1), mod)
    g_sub_inv = mod_inv(g_sub, mod)
    
    # 3. Порозрядний ліфтинг для знаходження цифр z_0, z_1, ..., z_{e-1}
    x = 0
    p_pow_j = 1
    for j in range(e):
        # h_cur = h_sub * (g_sub^(-1))^x mod mod
        h_cur = (h_sub * mod_pow(g_sub_inv, x, mod)) % mod
        
        # Ізолюючий степінь: target = (h_cur)^(p^(e - 1 - j)) mod mod
        iso_exp = p ** (e - 1 - j)
        target = mod_pow(h_cur, iso_exp, mod)
        
        # Знаходимо цифру z_j у групі простого порядку p
        z_j = solve_dlog_bsgs(gamma, target, p, mod)
        x += z_j * p_pow_j
        p_pow_j *= p
        
    return x

def crt(remainders: List[int], moduli: List[int]) -> int:
    """
    Китайська теорема про залишки: розв'язує систему порівнянь x ≡ remainders[i] (mod moduli[i]).
    Повертає єдиний розв'язок x за модулем добутку всіх moduli.
    """
    total_m = 1
    for m in moduli:
        total_m *= m
        
    x = 0
    for r, m in zip(remainders, moduli):
        m_i = total_m // m
        inv = mod_inv(m_i, m)
        x = (x + r * m_i * inv) % total_m
    return x

def pohlig_hellman(g: int, h: int, n: int, factors: List[Tuple[int, int]], mod: int) -> int:
    """
    Головна функція алгоритму Поліга — Геллмана.
    
    Параметри:
      g — твірний елемент групи (генератор)
      h — цільовий елемент (h = g^x mod mod)
      n — порядок циклічної групи (n = ord(g))
      factors — канонічний розклад порядку: список пар (p_i, e_i) такий, що n = prod(p_i^e_i)
      mod — модуль скінченного поля (для групи Z_mod^*)
      
    Повертає:
      Шуканий дискретний логарифм x ∈ [0, n - 1].
    """
    remainders = []
    moduli = []
    
    for p, e in factors:
        p_e = p ** e
        x_i = solve_prime_power_subgroup(g, h, p, e, n, mod)
        remainders.append(x_i)
        moduli.append(p_e)
        
    return crt(remainders, moduli)

# ── Демонстрація та верифікація ──────────────────────────────────────────────
if __name__ == "__main__":
    # Тест 1: Мультиплікативна група Z_31^* (модуль p_mod = 31, порядок n = 30 = 2*3*5)
    p_mod = 31
    n_order = 30
    prime_factors = [(2, 1), (3, 1), (5, 1)]
    generator = 3
    target_val = 13  # Шукаємо x такий, що 3^x ≡ 13 mod 31
    
    solved_x = pohlig_hellman(generator, target_val, n_order, prime_factors, p_mod)
    print(f"[Тест 1: Z_31^*] Знайдений показник x = {solved_x}")
    print(f"Перевірка: {generator}^{solved_x} mod {p_mod} = {mod_pow(generator, solved_x, p_mod)} (очікувалось: {target_val})")
    assert mod_pow(generator, solved_x, p_mod) == target_val
    
    # Тест 2: Група з кратними степенями простих множників (p_mod = 17, n = 16 = 2^4)
    p_mod2 = 17
    n_order2 = 16
    prime_factors2 = [(2, 4)]
    generator2 = 3
    target_val2 = 11  # Шукаємо x такий, що 3^x ≡ 11 mod 17
    
    solved_x2 = pohlig_hellman(generator2, target_val2, n_order2, prime_factors2, p_mod2)
    print(f"[Тест 2: Z_17^* (2^4)] Знайдений показник x = {solved_x2}")
    print(f"Перевірка: {generator2}^{solved_x2} mod {p_mod2} = {mod_pow(generator2, solved_x2, p_mod2)} (очікувалось: {target_val2})")
    assert mod_pow(generator2, solved_x2, p_mod2) == target_val2
    print("Усі автоматичні перевірки пройдено успішно!")
