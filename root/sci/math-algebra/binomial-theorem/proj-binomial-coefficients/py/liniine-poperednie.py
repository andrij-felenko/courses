MOD = 10**9 + 7

def precompute_factorials(max_n: int, p: int = MOD):
    """Попереднє обчислення факторіалів та обернених факторіалів за O(N)."""
    fact = [1] * (max_n + 1)
    inv_fact = [1] * (max_n + 1)
    
    for i in range(1, max_n + 1):
        fact[i] = (fact[i - 1] * i) % p
        
    # Модулярне обернення для N! за Малою теоремою Ферма O(log p)
    inv_fact[max_n] = pow(fact[max_n], p - 2, p)
    
    # Лінійне оновлення всіх попередніх обернених факторіалів O(N)
    for i in range(max_n - 1, -1, -1):
        inv_fact[i] = (inv_fact[i + 1] * (i + 1)) % p
        
    return fact, inv_fact

def ncr_mod(n: int, k: int, fact: list, inv_fact: list, p: int = MOD) -> int:
    """Запит C(n, k) mod p за O(1)."""
    if k < 0 or k > n:
        return 0
    return (fact[n] * inv_fact[k] % p) * inv_fact[n - k] % p
