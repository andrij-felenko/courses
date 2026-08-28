import math

def compute_convergents(alpha: float, max_terms: int = 10):
    """Обчислює підхідні дроби, абсолютну помилку та показник наближення mu для числа alpha."""
    convergents = []
    val = alpha
    p0, p1 = 0, 1
    q0, q1 = 1, 0

    for _ in range(max_terms):
        a = math.floor(val)
        p2 = a * p1 + p0
        q2 = a * q1 + q0

        if q2 > 1e15:
            break

        approx = p2 / q2
        err = abs(alpha - approx)
        mu = -math.log(err) / math.log(q2) if err > 0 and q2 > 1 else 0.0

        diff = val - a
        a_next = math.floor(1.0 / diff) if abs(diff) > 1e-12 else 0

        convergents.append((p2, q2, err, mu, a_next))

        p0, p1 = p1, p2
        q0, q1 = q1, q2

        if abs(diff) < 1e-12:
            break
        val = 1.0 / diff

    return convergents


def print_table(title: str, convergents: list):
    print(f"\n=== {title} ===")
    print(f"{'p':>12} {'q':>12} {'|alpha - p/q|':>18} {'Показник mu':>14} {'a_{n+1}':>12}")
    print("-" * 68)
    for p, q, err, mu, a_next in convergents:
        print(f"{p:12d} {q:12d} {err:18.5e} {mu:14.4f} {a_next:12d}")


if __name__ == "__main__":
    # 1. Квадратичне алгебраїчне число sqrt(2)
    sqrt2 = math.sqrt(2.0)
    print_table("Алгебраїчне число sqrt(2) (Теорема Рота: mu <= 2)", compute_convergents(sqrt2))

    # 2. Кубічне алгебраїчне число cbrt(2)
    cbrt2 = 2.0 ** (1.0 / 3.0)
    print_table("Алгебраїчне число cbrt(2) (Теорема Рота: mu <= 2)", compute_convergents(cbrt2))

    # 3. Золотий перетин phi = (1 + sqrt(5)) / 2
    phi = (1.0 + math.sqrt(5.0)) / 2.0
    print_table("Золотий перетин phi (Теорема Рота: mu -> 2 знізу)", compute_convergents(phi))

    # 4. Число Ліувіля L = sum 10^(-k!)
    liouville = sum(10.0 ** (-math.factorial(k)) for k in range(1, 7))
    print_table("Число Ліувіля L (Трансцендентне, mu -> inf)", compute_convergents(liouville))
