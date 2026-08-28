#include <iostream>
#include <complex>
#include <vector>
#include <optional>
#include <cmath>
#include <string>
#include <stdexcept>

using Complex = std::complex<double>;

enum class MobiusType {
    Parabolic,
    Elliptic,
    Hyperbolic,
    Loxodromic
};

class MobiusTransform {
private:
    Complex a_, b_, c_, d_;

public:
    MobiusTransform(Complex a, Complex b, Complex c, Complex d)
        : a_(a), b_(b), c_(c), d_(d) {}

    static MobiusTransform identity() {
        return MobiusTransform(1.0, 0.0, 0.0, 1.0);
    }

    Complex a() const { return a_; }
    Complex b() const { return b_; }
    Complex c() const { return c_; }
    Complex d() const { return d_; }

    Complex det() const {
        return a_ * d_ - b_ * c_;
    }

    MobiusTransform normalized() const {
        Complex d_val = det();
        Complex denom = std::sqrt(d_val);
        if (std::abs(denom) < 1e-15) {
            throw std::runtime_error("Вироджене перетворення Мьобіуса (det = 0)");
        }
        return MobiusTransform(a_ / denom, b_ / denom, c_ / denom, d_ / denom);
    }

    MobiusTransform operator*(const MobiusTransform& other) const {
        Complex a = a_ * other.a_ + b_ * other.c_;
        Complex b = a_ * other.b_ + b_ * other.d_;
        Complex c = c_ * other.a_ + d_ * other.c_;
        Complex d = c_ * other.b_ + d_ * other.d_;
        return MobiusTransform(a, b, c, d);
    }

    MobiusTransform inverse() const {
        MobiusTransform norm = normalized();
        return MobiusTransform(norm.d_, -norm.b_, -norm.c_, norm.a_);
    }

    std::optional<Complex> operator()(Complex z) const {
        Complex denom = c_ * z + d_;
        if (std::abs(denom) < 1e-12) {
            return std::nullopt;
        }
        return (a_ * z + b_) / denom;
    }

    std::vector<Complex> fixedPoints() const {
        MobiusTransform n = normalized();
        std::vector<Complex> pts;

        if (std::abs(n.c_) < 1e-12) {
            if (std::abs(n.a_ - n.d_) > 1e-12) {
                pts.push_back(n.b_ / (n.d_ - n.a_));
            }
            return pts;
        }

        Complex A = n.c_;
        Complex B = n.d_ - n.a_;
        Complex C = -n.b_;
        Complex disc = B * B - 4.0 * A * C;
        Complex sqrt_disc = std::sqrt(disc);

        pts.push_back((-B + sqrt_disc) / (2.0 * A));
        pts.push_back((-B - sqrt_disc) / (2.0 * A));
        return pts;
    }

    MobiusType type() const {
        MobiusTransform n = normalized();
        Complex tr = n.a_ + n.d_;
        Complex tr2 = tr * tr;

        double im_part = tr2.imag();
        double re_part = tr2.real();

        if (std::abs(im_part) < 1e-9) {
            if (std::abs(re_part - 4.0) < 1e-9) return MobiusType::Parabolic;
            if (re_part >= 0.0 && re_part < 4.0) return MobiusType::Elliptic;
            if (re_part > 4.0) return MobiusType::Hyperbolic;
        }
        return MobiusType::Loxodromic;
    }

    std::string typeName() const {
        switch (type()) {
            case MobiusType::Parabolic:  return "Параболічне";
            case MobiusType::Elliptic:   return "Еліптичне";
            case MobiusType::Hyperbolic: return "Гіперболічне";
            case MobiusType::Loxodromic: return "Локсодромне";
        }
        return "Невідомо";
    }
};

int main() {
    try {
        std::cout << "--- Тест перетворення Мьобіуса (C++) ---\n";
        MobiusTransform m(1.0, -1.0, 1.0, 1.0);
        MobiusTransform norm = m.normalized();

        std::cout << "Визначник: " << norm.det() << "\n";

        Complex z(2.0, 3.0);
        auto w = norm(z);
        if (w) {
            std::cout << "f(2 + 3i) = " << *w << "\n";
        } else {
            std::cout << "f(2 + 3i) = Infinity\n";
        }

        auto fixed = norm.fixedPoints();
        std::cout << "Знайдено нерухомих точок: " << fixed.size() << "\n";
        for (size_t i = 0; i < fixed.size(); ++i) {
            std::cout << "  z_" << (i + 1) << " = " << fixed[i] << "\n";
        }

        std::cout << "Тип перетворення: " << norm.typeName() << "\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
    }
    return 0;
}
