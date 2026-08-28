#include <iostream>
#include <array>
#include <cstdint>
#include <expected>
#include <concepts>

namespace crypto::pairing {

// Скінченне поле F_p у стилі C++20
template <std::int32_t Modulus>
class FieldElement {
private:
    std::int32_t val_{0};

    static constexpr std::int32_t normalize(std::int32_t v) noexcept {
        v %= Modulus;
        return v < 0 ? v + Modulus : v;
    }

public:
    constexpr FieldElement() noexcept = default;
    constexpr explicit FieldElement(std::int32_t v) noexcept : val_(normalize(v)) {}

    [[nodiscard]] constexpr std::int32_t value() const noexcept { return val_; }

    constexpr FieldElement operator+(const FieldElement& rhs) const noexcept {
        return FieldElement(val_ + rhs.val_);
    }

    constexpr FieldElement operator-(const FieldElement& rhs) const noexcept {
        return FieldElement(val_ - rhs.val_);
    }

    constexpr FieldElement operator*(const FieldElement& rhs) const noexcept {
        return FieldElement(val_ * rhs.val_);
    }

    [[nodiscard]] constexpr FieldElement invert() const {
        std::int32_t a = val_;
        for (std::int32_t x = 1; x < Modulus; ++x) {
            if ((a * x) % Modulus == 1) return FieldElement(x);
        }
        return FieldElement(0);
    }
};

using Fp = FieldElement<19>;

// Квадратичне розширення F_{p^2}
class Fp2 {
public:
    Fp re{0};
    Fp im{0};

    constexpr Fp2() noexcept = default;
    constexpr Fp2(Fp real, Fp imag) noexcept : re(real), im(imag) {}
    constexpr Fp2(std::int32_t real, std::int32_t imag) noexcept : re(real), im(imag) {}

    constexpr Fp2 operator+(const Fp2& rhs) const noexcept {
        return Fp2(re + rhs.re, im + rhs.im);
    }

    constexpr Fp2 operator-(const Fp2& rhs) const noexcept {
        return Fp2(re - rhs.re, im - rhs.im);
    }

    constexpr Fp2 operator*(const Fp2& rhs) const noexcept {
        // (a + bi)(c + di) = (ac - bd) + (ad + bc)i
        return Fp2(re * rhs.re - im * rhs.im, re * rhs.im + im * rhs.re);
    }

    [[nodiscard]] constexpr Fp2 square() const noexcept {
        return *this * *this;
    }

    [[nodiscard]] constexpr Fp2 invert() const {
        Fp norm = (re * re) + (im * im);
        Fp inv_norm = norm.invert();
        return Fp2(re * inv_norm, Fp(0) - (im * inv_norm));
    }
};

struct PointG2 {
    Fp2 x{};
    Fp2 y{};
    bool infinity{false};
};

class TatePairingEngine {
public:
    static Fp2 eval_line_step(PointG2& T, const PointG2* P, const PointG2& Q) {
        if (T.infinity) return Fp2(1, 0);

        Fp2 lambda;
        if (P == nullptr) { // Подвоєння точки
            Fp2 num = Fp2(3, 0) * T.x.square();
            Fp2 den = Fp2(2, 0) * T.y;
            lambda = num * den.invert();
        } else { // Додавання точок
            Fp2 num = P->y - T.y;
            Fp2 den = P->x - T.x;
            lambda = num * den.invert();
        }

        Fp2 dx = Q.x - T.x;
        Fp2 dy = Q.y - T.y;
        Fp2 line_val = dy - (lambda * dx);

        // Оновлюємо T = T + P
        Fp2 x3 = lambda.square() - T.x - (P ? P->x : T.x);
        Fp2 y3 = (lambda * (T.x - x3)) - T.y;
        T.x = x3;
        T.y = y3;

        return line_val;
    }

    static Fp2 final_exponentiation(Fp2 f, std::int32_t r) {
        std::int32_t exp = (19 * 19 - 1) / r;
        Fp2 res(1, 0);
        Fp2 base = f;

        while (exp > 0) {
            if (exp & 1) res = res * base;
            base = base.square();
            exp >>= 1;
        }
        return res;
    }

    static Fp2 compute(PointG2 P, PointG2 Q, std::int32_t r) {
        PointG2 T = P;
        Fp2 f(1, 0);

        for (int i = 1; i >= 0; --i) {
            Fp2 l_double = eval_line_step(T, nullptr, Q);
            f = f.square() * l_double;

            if (i == 0) {
                Fp2 l_add = eval_line_step(T, &P, Q);
                f = f * l_add;
            }
        }

        return final_exponentiation(f, r);
    }
};

} // namespace crypto::pairing

int main() {
    using namespace crypto::pairing;

    PointG2 P{ Fp2(0, 0), Fp2(1, 0), false };
    PointG2 Q{ Fp2(8, 0), Fp2(0, 6), false };

    Fp2 result = TatePairingEngine::compute(P, Q, 3);
    std::cout << "Спарювання (C++20): " << result.re.value() 
              << " + " << result.im.value() << "*i\n";
    return 0;
}
