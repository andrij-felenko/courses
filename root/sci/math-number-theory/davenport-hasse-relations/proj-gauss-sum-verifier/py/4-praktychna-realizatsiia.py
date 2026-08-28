import math
import cmath

def verify_davenport_hasse(p=7, s=2):
    """
    Верифікатор співвідношення підйому Девенпорта-Хассе над F_p^s.
    Для p=7, s=2 розширення F_49 конструюється через непривідний многочлен X^2 + 1.
    """
    # 1. Знаходимо первісний корінь g поля F_p
    g_base = 3  # Generator for F_7*
    
    # 2. Визначаємо кубічний характер (порядок m = 3)
    # chi(g_base^k) = exp(2 * pi * i * k / 3)
    def chi_base(x):
        if x % p == 0:
            return 0.0 + 0.0j
        # Знаходимо дискретний логарифм k за основою g_base
        val = x % p
        curr = 1
        k = 0
        while curr != val and k < p - 1:
            curr = (curr * g_base) % p
            k += 1
        angle = 2.0 * math.pi * (k % 3) / 3.0
        return cmath.exp(1j * angle)

    # 3. Адитивний характер psi(x) = exp(2 * pi * i * x / p)
    def psi_base(x):
        angle = 2.0 * math.pi * (x % p) / p
        return cmath.exp(1j * angle)

    # 4. Обчислюємо базову суму Гаусса g(chi, psi) у F_q
    g_small = sum(chi_base(x) * psi_base(x) for x in range(1, p))
    
    print(f"Базова сума Гаусса g(χ, ψ) = {g_small:.5f}")
    print(f"Модуль |g(χ, ψ)| = {abs(g_small):.5f} (Очікується √{p} = {math.sqrt(p):.5f})")

    # 5. Реалізуємо розширення F_q^s = F_49 як u + v*i (mod 7)
    # Norm(u + v*i) = u^2 + v^2 (mod 7)
    # Tr(u + v*i) = 2*u (mod 7)
    def norm_ext(u, v):
        return (u * u + v * v) % p

    def trace_ext(u, v):
        return (2 * u) % p

    # 6. Обчислюємо підняту суму Гаусса g(chi', psi') у F_49
    g_lifted = 0.0 + 0.0j
    for u in range(p):
        for v in range(p):
            if u == 0 and v == 0:
                continue
            n_val = norm_ext(u, v)
            t_val = trace_ext(u, v)
            g_lifted += chi_base(n_val) * psi_base(t_val)

    print(f"\nПіднята сума Гаусса g(χ', ψ') у F_49 = {g_lifted:.5f}")
    print(f"Модуль |g(χ', ψ')| = {abs(g_lifted):.5f} (Очікується {p} = {p:.5f})")

    # 7. Перевіряємо формулу підйому: g(χ', ψ') = (-1)^(s-1) * (g(χ, ψ))^s
    sign_factor = (-1) ** (s - 1)
    predicted_lifted = sign_factor * (g_small ** s)

    diff = abs(g_lifted - predicted_lifted)
    print(f"\nПрогнозоване значення (-1)^(s-1) * g(χ,ψ)^s = {predicted_lifted:.5f}")
    print(f"Абсолютна різниця |g_lifted - predicted| = {diff:.9e}")

    if diff < 1e-7:
        print("УСПІХ: Співвідношення Девенпорта-Хассе підтверджено!")
    else:
        print("ПОМИЛКА: Незбіг значень!")

if __name__ == "__main__":
    verify_davenport_hasse(p=7, s=2)
