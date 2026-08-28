#include <cstdint>
#include <optional>

struct Bezout {
    std::int64_t d, x, y;          // d = НСД(a, b),  a·x + b·y = d
};

Bezout ext_gcd(std::int64_t a, std::int64_t b) {
    std::int64_t r0 = a, r1 = b;
    std::int64_t x0 = 1, x1 = 0;
    std::int64_t y0 = 0, y1 = 1;
    while (r1 != 0) {
        const std::int64_t q = r0 / r1;
        std::int64_t t;
        t = r0 - q * r1;  r0 = r1;  r1 = t;
        t = x0 - q * x1;  x0 = x1;  x1 = t;
        t = y0 - q * y1;  y0 = y1;  y1 = t;
    }
    return { r0, x0, y0 };
}

// Обернене до a за модулем m; порожньо, якщо НСД(a, m) ≠ 1.
std::optional<std::int64_t> mod_inverse(std::int64_t a, std::int64_t m) {
    const Bezout r = ext_gcd(((a % m) + m) % m, m);
    if (r.d != 1) return std::nullopt;
    return ((r.x % m) + m) % m;    // ← подвійний % не косметика, а необхідність
}
