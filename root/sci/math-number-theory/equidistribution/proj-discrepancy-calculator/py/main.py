import math

def compute_star_discrepancy(pts: list[float]) -> float:
    """Обчислення зіркової дискрепантності D*N за O(N log N)."""
    if not pts:
        return 0.0
    
    # Нормалізація та сортування
    sorted_pts = sorted([x % 1.0 for x in pts])
    n = len(sorted_pts)
    inv_n = 1.0 / n
    
    max_diff = 0.0
    for i, x in enumerate(sorted_pts):
        diff1 = abs((i + 1) * inv_n - x)
        diff2 = abs(i * inv_n - x)
        if diff1 > max_diff:
            max_diff = diff1
        if diff2 > max_diff:
            max_diff = diff2
            
    return max_diff

def compute_weyl_sum(pts: list[float], h: int) -> float:
    """Обчислення тригонометричної суми Вейля (1/N) * |sum e^(2pi i h x_n)|."""
    if not pts:
        return 0.0
    
    two_pi = 2.0 * math.pi
    re_sum = sum(math.cos(two_pi * h * x) for x in pts)
    im_sum = sum(math.sin(two_pi * h * x) for x in pts)
    
    return math.hypot(re_sum, im_sum) / len(pts)

def van_der_corput(n: int, base: int = 2) -> float:
    """Генератор послідовності Ван дер Корпута."""
    q, bk = 0.0, 1.0 / base
    while n > 0:
        q += (n % base) * bk
        n //= base
        bk /= base
    return q

if __name__ == "__main__":
    N = 1000
    phi = (math.sqrt(5) - 1) / 2
    
    golden_seq = [(i * phi) % 1.0 for i in range(1, N + 1)]
    vdc_seq = [van_der_corput(i, 2) for i in range(1, N + 1)]
    
    print(f"Дискрепантність {{n*phi}} (N={N}): {compute_star_discrepancy(golden_seq):.6f}")
    print(f"Дискрепантність Ван дер Корпута (N={N}): {compute_star_discrepancy(vdc_seq):.6f}")
    print(f"Сума Вейля |S_N(1)|/N для {{n*phi}}: {compute_weyl_sum(golden_seq, 1):.6f}")
