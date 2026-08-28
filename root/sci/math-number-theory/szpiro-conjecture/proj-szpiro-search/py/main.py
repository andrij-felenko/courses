import math
from functools import reduce

def prime_factors(n):
    """Повертає множину унікальних простих дільників числа n."""
    factors = set()
    d = 2
    temp = abs(n)
    while d * d <= temp:
        if temp % d == 0:
            factors.add(d)
            while temp % d == 0:
                temp //= d
        d += 1
    if temp > 1:
        factors.add(temp)
    return factors

def radical(n):
    """Обчислює радикал натурального числа (добуток унікальних простих дільників)."""
    factors = prime_factors(n)
    return reduce(lambda x, y: x * y, factors, 1)

def analyze_frey_curve(a, b):
    """Обчислює дискримінант, провідник та індекс Шпіро для кривої Фрея y² = x(x-a)(x+b)."""
    if math.gcd(a, b) != 1:
        return None
    c = a + b
    abc = a * b * c
    
    # Дискримінант кривої Фрея
    disc = 16 * (abc ** 2)
    
    # Радикал добутку abc
    rad_abc = radical(abc)
    
    # Оцінка провідника (з урахуванням оцінки для p=2)
    conductor = rad_abc
    if abc % 2 != 0:
        conductor *= 2
        
    sigma = math.log(abs(disc)) / math.log(conductor)
    
    return {
        'a': a, 'b': b, 'c': c,
        'disc': disc,
        'rad': rad_abc,
        'conductor': conductor,
        'sigma': sigma
    }

def scan_frey_range(max_a, max_b, min_sigma=1.1):
    """Сканує діапазон a та b у пошуках кривих із високим індексом Шпіро."""
    results = []
    for a in range(1, max_a):
        for b in range(a + 1, max_b):
            res = analyze_frey_curve(a, b)
            if res and res['sigma'] >= min_sigma:
                results.append(res)
    results.sort(key=lambda x: x['sigma'], reverse=True)
    return results

if __name__ == '__main__':
    # Приклад обчислення для відомої трійки Решата (1 + 4374 = 4375)
    rec = analyze_frey_curve(1, 4374)
    print(f"Трійка 1 + 4374 = 4375:")
    print(f"  Дискримінант log|Δ| = {math.log(rec['disc']):.4f}")
    print(f"  Провідник log N_E = {math.log(rec['conductor']):.4f}")
    print(f"  Індекс Шпіро σ(E) = {rec['sigma']:.4f}")
