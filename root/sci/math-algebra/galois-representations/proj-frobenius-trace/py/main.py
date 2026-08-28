def count_points_mod_p(a1, a2, a3, a4, a6, p):
    """Підрахунок кількості точок E(F_p) для кривої у формі Вейєрштрасса."""
    if p == 2:
        count = 1  # точка O на нескінченності
        for x in range(2):
            for y in range(2):
                lhs = (y * y + a1 * x * y + a3 * y) % 2
                rhs = (x * x * x + a2 * x * x + a4 * x + a6) % 2
                if lhs == rhs:
                    count += 1
        return count

    # Перехід до Y^2 = 4x^3 + b2 x^2 + 2b4 x + b6
    b2 = (a1 * a1 + 4 * a2) % p
    b4 = (a1 * a3 + 2 * a4) % p
    b6 = (a3 * a3 + 4 * a6) % p

    # Попередній розрахунок таблиці кількості квадратних коренів
    sq_roots = [0] * p
    for y in range(p):
        sq_roots[(y * y) % p] += 1

    count = 1  # нескінченно віддалена точка O
    for x in range(p):
        rhs = (4 * x * x * x + b2 * x * x + 2 * b4 * x + b6) % p
        count += sq_roots[rhs]

    return count


def expand_modular_form(max_n):
    """Розгортання добутку f(q) = q * prod (1 - q^n)^2 * (1 - q^11n)^2 у степеневий ряд."""
    poly = [0] * (max_n + 1)
    poly[0] = 1

    def apply_factor(poly, shift):
        """Множення многочлена на (1 - q^shift) за модулем q^(max_n + 1)."""
        new_p = list(poly)
        for i in range(shift, max_n + 1):
            new_p[i] -= poly[i - shift]
        return new_p

    # Множимо двічі на (1 - q^n) для кожного n
    for n in range(1, max_n + 1):
        poly = apply_factor(poly, n)
        poly = apply_factor(poly, n)

    # Множимо двічі на (1 - q^(11n)) для кожного n
    for n in range(1, max_n // 11 + 1):
        poly = apply_factor(poly, 11 * n)
        poly = apply_factor(poly, 11 * n)

    # a_n(f) відповідає коефіцієнту при q^(n-1) у poly
    coeffs = [0] * (max_n + 1)
    for n in range(1, max_n + 1):
        coeffs[n] = poly[n - 1]
    return coeffs


def is_prime(n):
    if n < 2:
        return False
    for d in range(2, int(n**0.5) + 1):
        if n % d == 0:
            return False
    return True


if __name__ == "__main__":
    # Параметри кривої 11a1 (X_0(11)): y^2 + y = x^3 - x^2 - 10x - 20
    a1, a2, a3, a4, a6 = 0, -1, 1, -10, -20
    max_p = 50

    q_coeffs = expand_modular_form(max_p)

    print(f"{'Просте p':<10}{'#E(F_p)':<12}{'Слід a_p(E)':<16}{'Коеф. a_p(f)':<16}{'Збіг?':<10}")
    print("-" * 64)

    primes = [p for p in range(2, max_p + 1) if is_prime(p)]
    for p in primes:
        if p == 11:
            ap_curve = -1  # просте число поганої мультиплікативної редукції
            pts_str = "погана ред."
        else:
            pts = count_points_mod_p(a1, a2, a3, a4, a6, p)
            ap_curve = p + 1 - pts
            pts_str = str(pts)

        ap_form = q_coeffs[p]
        match = "✓ ТАК" if ap_curve == ap_form else "✗ НІ"
        print(f"{p:<10}{pts_str:<12}{ap_curve:<16}{ap_form:<16}{match:<10}")
