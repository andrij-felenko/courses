#include <iostream>
#include <optional>
#include <cstdint>

constexpr int64_t P_PRIME = 431;

struct Fp2 {
    int64_t re{0}, im{0};
    constexpr Fp2() = default;
    constexpr Fp2(int64_t r, int64_t i = 0) : re((r % P_PRIME + P_PRIME) % P_PRIME), im((i % P_PRIME + P_PRIME) % P_PRIME) {}

    constexpr bool operator==(const Fp2& o) const = default;
    constexpr Fp2 operator+(const Fp2& o) const { return { re + o.re, im + o.im }; }
    constexpr Fp2 operator-(const Fp2& o) const { return { re - o.re, im - o.im }; }
    constexpr Fp2 operator*(const Fp2& o) const { return { re * o.re - im * o.im, re * o.im + im * o.re }; }

    constexpr Fp2 inv() const {
        int64_t norm = (re * re + im * im) % P_PRIME;
        int64_t res = 1, b = norm, exp = P_PRIME - 2;
        while (exp > 0) { if (exp & 1) res = (res * b) % P_PRIME; b = (b * b) % P_PRIME; exp >>= 1; }
        return { re * res, -im * res };
    }
};

class EllipticCurve {
public:
    Fp2 a, b;
    constexpr EllipticCurve(Fp2 a_val, Fp2 b_val) : a(a_val), b(b_val) {}

    [[nodiscard]] std::optional<Fp2> j_invariant() const noexcept {
        Fp2 a3 = a * a * a, b2 = b * b;
        Fp2 num = Fp2(1728) * (Fp2(4) * a3);
        Fp2 den = (Fp2(4) * a3) + (Fp2(27) * b2);
        if (den == Fp2(0, 0)) return std::nullopt;
        return num * den.inv();
    }
};

int main() {
    std::cout << "=== Демонстрація C++20 API libjinv ===\n";
    EllipticCurve e1(Fp2(1), Fp2(0));
    if (auto j = e1.j_invariant()) {
        std::cout << "Крива y^2 = x^3 + x -> j = " << j->re << " (очікується: " << 1728 % P_PRIME << ")\n";
    }
    return 0;
}
