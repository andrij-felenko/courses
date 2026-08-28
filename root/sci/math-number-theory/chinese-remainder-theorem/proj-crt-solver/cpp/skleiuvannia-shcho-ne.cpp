#include <cstdint>
#include <numeric>      // std::gcd
#include <optional>
#include <vector>

struct Cong { int64_t a, n; };        // x ≡ a (mod n)

// розширений Евклід: НСД(a, b) плюс x, y такі, що a·x + b·y = НСД(a, b)
static int64_t egcd(int64_t a, int64_t b, int64_t &x, int64_t &y) {
    if (b == 0) { x = 1; y = 0; return a; }
    int64_t x1, y1;
    int64_t g = egcd(b, a % b, x1, y1);
    x = y1;
    y = x1 - (a / b) * y1;
    return g;
}

static int64_t inv_mod(int64_t a, int64_t m) {
    int64_t x, y;
    egcd((a % m + m) % m, m, x, y);
    return (x % m + m) % m;            // egcd може дати від'ємний x — нормалізуємо
}

std::optional<Cong> crt_pair(Cong u, Cong v) {
    int64_t g = std::gcd(u.n, v.n);
    int64_t diff = v.a - u.a;
    if (diff % g != 0) return std::nullopt;          // умова сумісності не виконана
    int64_t m = v.n / g;                             // модуль, за яким шукаємо t
    int64_t lcm = u.n * m;                           // ділили ДО множення: це НСК, не добуток
    // (diff/g mod m) · inv — обидва множники менші за m, добуток менший за m²
    int64_t t = (int64_t)((__int128)(diff / g) % m * inv_mod(u.n / g, m) % m);
    if (t < 0) t += m;
    __int128 x = (__int128)u.n * t + u.a;            // < НСК + n₁ — тільки тут потрібні 128 біт
    return Cong{ (int64_t)((x % lcm + lcm) % lcm), lcm };
}

std::optional<Cong> crt(const std::vector<int64_t> &res, const std::vector<int64_t> &mod) {
    Cong acc{0, 1};                                  // x ≡ 0 (mod 1) — істинне для всіх x
    for (size_t i = 0; i < mod.size(); ++i) {
        auto merged = crt_pair(acc, Cong{res[i] % mod[i], mod[i]});
        if (!merged) return std::nullopt;
        acc = *merged;
    }
    return acc;
}
