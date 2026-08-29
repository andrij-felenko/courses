#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <cstdint>
#include <cmath>

class Rational {
private:
    std::int64_t m_num;
    std::int64_t m_den;

    void normalize() {
        if (m_den == 0) {
            throw std::invalid_argument("Знаменник дробу не може дорівнювати нулю!");
        }
        if (m_den < 0) {
            m_num = -m_num;
            m_den = -m_den;
        }
        std::int64_t g = std::gcd(m_num, m_den);
        m_num /= g;
        m_den /= g;
    }

public:
    constexpr Rational() noexcept : m_num(0), m_den(1) {}

    Rational(std::int64_t num, std::int64_t den = 1) : m_num(num), m_den(den) {
        normalize();
    }

    constexpr std::int64_t num() const noexcept { return m_num; }
    constexpr std::int64_t den() const noexcept { return m_den; }

    Rational operator-() const {
        return Rational(-m_num, m_den);
    }

    Rational abs() const {
        return Rational(m_num < 0 ? -m_num : m_num, m_den);
    }

    Rational operator+(const Rational& rhs) const {
        std::int64_t g = std::gcd(m_den, rhs.m_den);
        std::int64_t b_prime = m_den / g;
        std::int64_t d_prime = rhs.m_den / g;

        std::int64_t n = m_num * d_prime + rhs.m_num * b_prime;
        std::int64_t d = m_den * d_prime;
        return Rational(n, d);
    }

    Rational operator-(const Rational& rhs) const {
        return *this + (-rhs);
    }

    Rational operator*(const Rational& rhs) const {
        std::int64_t g1 = std::gcd(m_num, rhs.m_den);
        std::int64_t g2 = std::gcd(rhs.m_num, m_den);

        std::int64_t n = (m_num / g1) * (rhs.m_num / g2);
        std::int64_t d = (m_den / g2) * (rhs.m_den / g1);
        return Rational(n, d);
    }

    Rational operator/(const Rational& rhs) const {
        if (rhs.m_num == 0) {
            throw std::domain_error("Ділення на нульовий дріб!");
        }
        return *this * Rational(rhs.m_den, rhs.m_num);
    }

    Rational& operator+=(const Rational& rhs) {
        *this = *this + rhs;
        return *this;
    }

    Rational& operator-=(const Rational& rhs) {
        *this = *this - rhs;
        return *this;
    }

    Rational& operator*=(const Rational& rhs) {
        *this = *this * rhs;
        return *this;
    }

    Rational& operator/=(const Rational& rhs) {
        *this = *this / rhs;
        return *this;
    }

    Rational pow(int exp) const {
        if (exp == 0) return Rational(1, 1);
        if (exp < 0) {
            if (m_num == 0) throw std::domain_error("Піднесення нуля до від'ємного степеня!");
            return Rational(m_den, m_num).pow(-exp);
        }

        Rational base = *this;
        Rational result(1, 1);
        int e = exp;
        while (e > 0) {
            if (e % 2 == 1) {
                result *= base;
            }
            base *= base;
            e /= 2;
        }
        return result;
    }

    bool operator==(const Rational& rhs) const noexcept {
        return m_num == rhs.m_num && m_den == rhs.m_den;
    }

    bool operator!=(const Rational& rhs) const noexcept {
        return !(*this == rhs);
    }

    bool operator<(const Rational& rhs) const noexcept {
        if (m_num == rhs.m_num && m_den == rhs.m_den) return false;
        int s1 = m_num < 0 ? -1 : (m_num > 0 ? 1 : 0);
        int s2 = rhs.m_num < 0 ? -1 : (rhs.m_num > 0 ? 1 : 0);
        if (s1 != s2) return s1 < s2;
        if (s1 == 0) return false;

        std::int64_t a = std::abs(m_num);
        std::int64_t b = m_den;
        std::int64_t c = std::abs(rhs.m_num);
        std::int64_t d = rhs.m_den;

        while (true) {
            std::int64_t q1 = a / b;
            std::int64_t q2 = c / d;
            if (q1 != q2) {
                return (s1 > 0) ? (q1 < q2) : (q1 > q2);
            }
            std::int64_t r1 = a % b;
            std::int64_t r2 = c % d;
            if (r1 == 0 || r2 == 0) {
                if (r1 == 0 && r2 == 0) return false;
                return (s1 > 0) ? (r1 == 0) : (r2 == 0);
            }
            a = d;
            b = r2;
            c = b;
            d = r1;
        }
    }

    bool operator<=(const Rational& rhs) const noexcept {
        return *this < rhs || *this == rhs;
    }

    bool operator>(const Rational& rhs) const noexcept {
        return !(*this <= rhs);
    }

    bool operator>=(const Rational& rhs) const noexcept {
        return !(*this < rhs);
    }

    explicit operator double() const noexcept {
        return static_cast<double>(m_num) / static_cast<double>(m_den);
    }

    std::string to_string() const {
        if (m_den == 1) return std::to_string(m_num);
        return std::to_string(m_num) + "/" + std::to_string(m_den);
    }
};

std::ostream& operator<<(std::ostream& os, const Rational& r) {
    return os << r.to_string();
}

int main() {
    try {
        std::cout << "--- Тестування раціональної арифметики мовою C++ ---\n";
        Rational a(7, 12);
        Rational b(5, 18);

        std::cout << "a = " << a << ", b = " << b << "\n";
        std::cout << "a + b = " << (a + b) << " (очікувано 31/36)\n";
        std::cout << "a - b = " << (a - b) << " (очікувано 11/36)\n";
        std::cout << "a * b = " << (a * b) << " (очікувано 35/216)\n";
        std::cout << "a / b = " << (a / b) << " (очікувано 21/10)\n";

        Rational c(2, 3);
        std::cout << "(2/3)^3 = " << c.pow(3) << " (очікувано 8/27)\n";
        std::cout << "(2/3)^(-2) = " << c.pow(-2) << " (очікувано 9/4)\n";

        std::cout << "a < b: " << (a < b ? "true" : "false") << "\n";
        std::cout << "a > b: " << (a > b ? "true" : "false") << "\n";
        std::cout << "a == Rational(14, 24): " << (a == Rational(14, 24) ? "true" : "false") << "\n";

        std::cout << "double(a) = " << static_cast<double>(a) << "\n";

        try {
            Rational bad(1, 0);
        } catch (const std::invalid_argument& ex) {
            std::cout << "Перехоплено виняток для нульового знаменника: " << ex.what() << "\n";
        }

        try {
            Rational zero(0, 1);
            Rational div_zero = a / zero;
        } catch (const std::domain_error& ex) {
            std::cout << "Перехоплено виняток ділення на нуль: " << ex.what() << "\n";
        }

    } catch (const std::exception& ex) {
        std::cerr << "Непередбачена помилка: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
