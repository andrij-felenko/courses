import math

def generate_perfect_powers(limit: int) -> list[tuple[int, int, int]]:
    """
    Генерує всі точні степені u^v <= limit для u >= 2, v >= 2.
    Повертає відсортований список кортежів (значення, основа, показник).
    """
    powers = []
    seen = set()
    
    max_u = math.isqrt(limit) + 1
    for u in range(2, max_u + 1):
        val = u * u
        v = 2
        while val <= limit:
            if val not in seen:
                seen.add(val)
                powers.append((val, u, v))
            val *= u
            v += 1

    powers.sort(key=lambda item: item[0])
    return powers

def find_consecutive_powers(limit: int) -> list[dict]:
    """
    Шукає всі пари сусідніх точних степенів з різницею 1 до заданої межі limit.
    """
    powers = generate_perfect_powers(limit)
    solutions = []
    
    for i in range(len(powers) - 1):
        val1, u1, v1 = powers[i]
        val2, u2, v2 = powers[i + 1]
        
        if val2 - val1 == 1:
            solutions.append({
                "x": u2, "a": v2, "y": u1, "b": v1,
                "eq": f"{u2}^{v2} - {u1}^{v1} = {val2} - {val1} = 1"
            })
            
    return solutions

def is_wieferich_pair(p: int, q: int) -> bool:
    """
    Перевіряє, чи утворюють прості числа p і q взаємну пару Віферіха:
    p^(q-1) ≡ 1 (mod q²)  та  q^(p-1) ≡ 1 (mod p²).
    """
    if p <= 1 or q <= 1 or p == q:
        return False
    cond1 = pow(p, q - 1, q * q) == 1
    cond2 = pow(q, p - 1, p * p) == 1
    return cond1 and cond2

if __name__ == "__main__":
    search_limit = 100000
    print(f"Пошук сусідніх степенів до N = {search_limit}...")
    results = find_consecutive_powers(search_limit)
    for res in results:
        print(f"Знайдено розв'язок: {res['eq']}")
        
    p, q = 3, 2
    print(f"Перевірка умови Віферіха для p={p}, q={q}: {is_wieferich_pair(p, q)}")
