#include <cstdint>
#include <iomanip>
#include <iostream>

using u64 = std::uint64_t;

// сума ВСІХ дільників n — прямим перебором, без жодного знання про будову n
u64 sigma(u64 n) {
    u64 sum = 0;
    for (u64 d = 1; d * d <= n; ++d) {          // дільники ходять парами d · (n/d)
        if (n % d != 0) continue;
        sum += d;
        if (u64 pair = n / d; pair != d)        // квадратний корінь не подвоюємо
            sum += pair;
    }
    return sum;
}

bool is_prime(u64 n) {
    if (n < 2) return false;
    for (u64 d = 2; d * d <= n; ++d)
        if (n % d == 0) return false;
    return true;
}

int main() {
    for (unsigned p = 2; p <= 31; ++p) {
        if (!is_prime(p)) continue;                     // складене p — 2^p − 1 теж складене
        const u64 mersenne = (u64{1} << p) - 1;         // 2^p − 1
        if (!is_prime(mersenne)) continue;              // не просте — досконалого числа немає
        const u64 n = (u64{1} << (p - 1)) * mersenne;   // 2^(p−1)·(2^p − 1)

        const u64 s = sigma(n);                         // рахунок, незалежний від формули
        std::cout << "p=" << std::setw(2) << p
                  << "  N=" << std::setw(19) << n
                  << "  σ(N)=" << std::setw(19) << s
                  << (s == 2 * n ? "  ✓\n" : "  ✗\n");
    }
}
