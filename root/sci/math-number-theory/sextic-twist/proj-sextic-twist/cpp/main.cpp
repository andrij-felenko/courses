#include <iostream>
#include <array>
#include <expected>
#include <optional>
#include <cstdint>

namespace crypto {

// Модуль розширення 𝔽_p (демонстраційний)
constexpr std::int64_t kModulusP = 23;

class Fp {
private:
    std::int64_t val_{0};

    static constexpr std::int64_t normalize(std::int64_t v) noexcept {
        v %= kModulusP;
        return v < 0 ? v + kModulusP : v;
    }

public:
    constexpr Fp() noexcept = default;
    constexpr explicit Fp(std::int64_t v) noexcept : val_(normalize(v)) {}

    [[nodiscard]] constexpr std::int64_t value() const noexcept { return val_; }

    constexpr Fp operator+(Fp rhs) const noexcept { return Fp(val_ + rhs.val_); }
    constexpr Fp operator-(Fp rhs) const noexcept { return Fp(val_ - rhs.val_); }
    constexpr Fp operator*(Fp rhs) const noexcept { return Fp(val_ * rhs.val_); }

    constexpr bool operator==(Fp rhs) const noexcept { return val_ == rhs.val_; }
};

// Елемент полів 𝔽_{p^2} = c0 + c1 * u (u^2 = -1)
class Fp2 {
public:
    Fp c0{};
    Fp c1{};

    constexpr Fp2() noexcept = default;
    constexpr Fp2(Fp v0, Fp v1) noexcept : c0(v0), c1(v1) {}
    constexpr Fp2(std::int64_t v0, std::int64_t v1) noexcept : c0(v0), c1(v1) {}

    [[nodiscard]] constexpr Fp2 operator+(const Fp2& rhs) const noexcept {
        return {c0 + rhs.c0, c1 + rhs.c1};
    }

    [[nodiscard]] constexpr Fp2 operator-(const Fp2& rhs) const noexcept {
        return {c0 - rhs.c0, c1 - rhs.c1};
    }

    // Множення в 𝔽_{p^2}: (a0+a1*u)(b0+b1*u) = (a0*b0 - a1*b1) + (a0*b1 + a1*b0)*u
    [[nodiscard]] constexpr Fp2 operator*(const Fp2& rhs) const noexcept {
        Fp t0 = c0 * rhs.c0;
        Fp t1 = c1 * rhs.c1;
        Fp t2 = (c0 + c1) * (rhs.c0 + rhs.c1);
        return {t0 - t1, t2 - (t0 + t1)};
    }

    [[nodiscard]] constexpr Fp2 square() const noexcept {
        return *this * *this;
    }

    constexpr bool operator==(const Fp2& rhs) const noexcept {
        return c0 == rhs.c0 && c1 == rhs.c1;
    }
};

// Розтвістовані компоненти точки в 𝔽_{p^{12}}
struct UntwistedPoint {
    Fp2 x_coeff; // Зв'язано з w^2
    Fp2 y_coeff; // Зв'язано з w^3
};

enum class CurveError {
    kPointNotOnCurve,
    kInvalidCoordinates
};

// Точка на твістованій еліптичній кривій E'(𝔽_{p^2})
class G2Point {
private:
    Fp2 x_{};
    Fp2 y_{};
    bool is_infinity_{true};

public:
    constexpr G2Point() noexcept = default;

    static std::expected<G2Point, CurveError> create(Fp2 x, Fp2 y, Fp2 b_twist) noexcept {
        G2Point pt;
        pt.x_ = x;
        pt.y_ = y;
        pt.is_infinity_ = false;

        // Перевірка y'^2 == x'^3 + b_twist
        Fp2 lhs = y.square();
        Fp2 rhs = (x.square() * x) + b_twist;

        if (!(lhs == rhs)) {
            return std::unexpected(CurveError::kPointNotOnCurve);
        }
        return pt;
    }

    [[nodiscard]] constexpr bool is_infinity() const noexcept { return is_infinity_; }
    [[nodiscard]] constexpr const Fp2& x() const noexcept { return x_; }
    [[nodiscard]] constexpr const Fp2& y() const noexcept { return y_; }

    // Конвертація D-type розтвістування
    [[nodiscard]] constexpr UntwistedPoint untwist_d() const noexcept {
        if (is_infinity_) {
            return UntwistedPoint{Fp2{0, 0}, Fp2{0, 0}};
        }
        return UntwistedPoint{x_, y_};
    }
};

} // namespace crypto

int main() {
    using namespace crypto;

    Fp2 b_twist{4, 0};
    
    // Спроба створення точки
    auto point_result = G2Point::create(Fp2{1, 2}, Fp2{3, 4}, b_twist);

    if (!point_result) {
        std::cout << "Помилка створення точки: Точка не належить твістованій кривій!\n";
    } else {
        const auto& pt = *point_result;
        auto untwisted = pt.untwist_d();
        std::cout << "Точку успішно розтвістовано:\n";
        std::cout << "  x_coeff (w^2) = " << untwisted.x_coeff.c0.value() 
                  << " + " << untwisted.x_coeff.c1.value() << "*u\n";
    }

    return 0;
}
