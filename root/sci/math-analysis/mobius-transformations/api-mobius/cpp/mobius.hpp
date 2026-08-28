// mobius.hpp — Офіційний C++20/C++17 інтерфейс бібліотеки libmobius
#ifndef MOBIUS_HPP
#define MOBIUS_HPP

#include <complex>
#include <vector>
#include <optional>
#include <string>
#include <stdexcept>
#include <span>

namespace mobius {

using Complex = std::complex<double>;

class SingularMatrixException : public std::runtime_error {
public:
    explicit SingularMatrixException(const std::string& msg)
        : std::runtime_error(msg) {}
};

enum class MobiusType {
    Parabolic,
    Elliptic,
    Hyperbolic,
    Loxodromic
};

class Transform {
private:
    Complex a_, b_, c_, d_;

public:
    Transform(Complex a, Complex b, Complex c, Complex d)
        : a_(a), b_(b), c_(c), d_(d) {}

    static Transform identity() noexcept {
        return Transform(1.0, 0.0, 0.0, 1.0);
    }

    static Transform fromThreePoints(Complex z1, Complex z2, Complex z3,
                                      Complex w1, Complex w2, Complex w3);

    [[nodiscard]] Complex a() const noexcept { return a_; }
    [[nodiscard]] Complex b() const noexcept { return b_; }
    [[nodiscard]] Complex c() const noexcept { return c_; }
    [[nodiscard]] Complex d() const noexcept { return d_; }

    [[nodiscard]] Complex det() const noexcept {
        return a_ * d_ - b_ * c_;
    }

    [[nodiscard]] Complex trace() const noexcept {
        Transform n = normalized();
        return n.a_ + n.d_;
    }

    [[nodiscard]] Transform normalized() const {
        Complex d_val = det();
        Complex denom = std::sqrt(d_val);
        if (std::abs(denom) < 1e-15) {
            throw SingularMatrixException("Вироджене перетворення Мьобіуса: det = 0");
        }
        return Transform(a_ / denom, b_ / denom, c_ / denom, d_ / denom);
    }

    [[nodiscard]] Transform operator*(const Transform& other) const noexcept {
        Complex a = a_ * other.a_ + b_ * other.c_;
        Complex b = a_ * other.b_ + b_ * other.d_;
        Complex c = c_ * other.a_ + d_ * other.c_;
        Complex d = c_ * other.b_ + d_ * other.d_;
        return Transform(a, b, c, d);
    }

    [[nodiscard]] Transform inverse() const {
        Transform norm = normalized();
        return Transform(norm.d_, -norm.b_, -norm.c_, norm.a_);
    }

    [[nodiscard]] std::optional<Complex> operator()(Complex z) const noexcept {
        Complex denom = c_ * z + d_;
        if (std::abs(denom) < 1e-12) {
            return std::nullopt;
        }
        return (a_ * z + b_) / denom;
    }

    void transformBuffer(std::span<const Complex> in_points,
                         std::span<Complex> out_points,
                         std::span<bool> out_inf_flags) const;

    [[nodiscard]] std::vector<Complex> fixedPoints() const;
    [[nodiscard]] MobiusType type() const;
    [[nodiscard]] std::string typeName() const;
};

[[nodiscard]] Complex crossRatio(Complex z1, Complex z2, Complex z3, Complex z4) noexcept;

} // namespace mobius

#endif // MOBIUS_HPP
