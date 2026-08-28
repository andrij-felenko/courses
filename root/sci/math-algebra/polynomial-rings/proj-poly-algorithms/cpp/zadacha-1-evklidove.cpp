#include <iostream>
#include <vector>
#include <numeric>
#include <cmath>
#include <algorithm>
#include <stdexcept>

// Раціональне число (дріб) для точної арифметики без похибок із рухомою комою
struct Rational {
    long long num{0};
    long long den{1};

    Rational(long long n = 0, long long d = 1) : num(n), den(d) {
        if (den == 0) throw std::invalid_argument("Знаменник не може дорівнювати нулю");
        if (den < 0) { num = -num; den = -den; }
        long long g = std::gcd(std::abs(num), den);
        if (g > 0) { num /= g; den /= g; }
    }

    Rational operator+(const Rational& o) const { return {num * o.den + o.num * den, den * o.den}; }
    Rational operator-(const Rational& o) const { return {num * o.den - o.num * den, den * o.den}; }
    Rational operator*(const Rational& o) const { return {num * o.num, den * o.den}; }
    Rational operator/(const Rational& o) const { return {num * o.den, den * o.num}; }
    bool operator==(const Rational& o) const { return num == o.num && den == o.den; }
    bool operator!=(const Rational& o) const { return !(*this == o); }
    bool is_zero() const { return num == 0; }
};

class Polynomial {
public:
    std::vector<Rational> coeffs; // coeffs[i] — коефіцієнт при x^i

    Polynomial() = default;
    Polynomial(std::initializer_list<Rational> list) : coeffs(list) { normalize(); }
    explicit Polynomial(std::vector<Rational> c) : coeffs(std::move(c)) { normalize(); }

    void normalize() {
        while (coeffs.size() > 1 && coeffs.back().is_zero()) {
            coeffs.pop_back();
        }
        if (coeffs.empty()) coeffs.push_back(Rational(0));
    }

    int deg() const {
        return (coeffs.size() == 1 && coeffs[0].is_zero()) ? -1 : static_cast<int>(coeffs.size()) - 1;
    }

    bool is_zero() const { return deg() == -1; }

    Rational lead() const { return coeffs.back(); }

    Polynomial operator+(const Polynomial& o) const {
        size_t n = std::max(coeffs.size(), o.coeffs.size());
        std::vector<Rational> res(n, Rational(0));
        for (size_t i = 0; i < coeffs.size(); ++i) res[i] = res[i] + coeffs[i];
        for (size_t i = 0; i < o.coeffs.size(); ++i) res[i] = res[i] + o.coeffs[i];
        return Polynomial(res);
    }

    Polynomial operator-(const Polynomial& o) const {
        size_t n = std::max(coeffs.size(), o.coeffs.size());
        std::vector<Rational> res(n, Rational(0));
        for (size_t i = 0; i < coeffs.size(); ++i) res[i] = res[i] + coeffs[i];
        for (size_t i = 0; i < o.coeffs.size(); ++i) res[i] = res[i] - o.coeffs[i];
        return Polynomial(res);
    }

    Polynomial operator*(const Polynomial& o) const {
        if (is_zero() || o.is_zero()) return Polynomial({Rational(0)});
        std::vector<Rational> res(coeffs.size() + o.coeffs.size() - 1, Rational(0));
        for (size_t i = 0; i < coeffs.size(); ++i) {
            for (size_t j = 0; j < o.coeffs.size(); ++j) {
                res[i + j] = res[i + j] + (coeffs[i] * o.coeffs[j]);
            }
        }
        return Polynomial(res);
    }

    Polynomial operator*(const Rational& scalar) const {
        if (scalar.is_zero()) return Polynomial({Rational(0)});
        std::vector<Rational> res = coeffs;
        for (auto& c : res) c = c * scalar;
        return Polynomial(res);
    }
};

// Ділення з остачею: f = q * g + r
std::pair<Polynomial, Polynomial> div_rem(Polynomial f, const Polynomial& g) {
    if (g.is_zero()) throw std::invalid_argument("Ділення на нульовий многочлен");
    Polynomial q({Rational(0)});
    while (!f.is_zero() && f.deg() >= g.deg()) {
        int shift = f.deg() - g.deg();
        Rational factor = f.lead() / g.lead();
        std::vector<Rational> m_coeffs(shift + 1, Rational(0));
        m_coeffs[shift] = factor;
        Polynomial monom(m_coeffs);

        q = q + monom;
        f = f - (monom * g);
    }
    return {q, f};
}

// Розширений алгоритм Евкліда: знаходить gcd, u, v такі, що u*f + v*g = gcd (монічний)
struct BezoutResult {
    Polynomial gcd;
    Polynomial u;
    Polynomial v;
};

BezoutResult ext_gcd(Polynomial a, Polynomial b) {
    Polynomial u0({Rational(1)}), u1({Rational(0)});
    Polynomial v0({Rational(0)}), v1({Rational(1)});

    while (!b.is_zero()) {
        auto [q, r] = div_rem(a, b);
        a = b;
        b = r;

        Polynomial next_u = u0 - (q * u1);
        u0 = u1;
        u1 = next_u;

        Polynomial next_v = v0 - (q * v1);
        v0 = v1;
        v1 = next_v;
    }

    // Нормалізація до унітарного многочлена (старший коефіцієнт = 1)
    Rational lead_c = a.lead();
    Rational inv_c = Rational(1) / lead_c;
    return {a * inv_c, u0 * inv_c, v0 * inv_c};
}
