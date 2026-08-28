#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <cstdint>

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

    Rational(std::int64_t num, std::int64_t den) : m_num(num), m_den(den) {
        normalize();
    }

    constexpr std::int64_t num() const noexcept { return m_num; }
    constexpr std::int64_t den() const noexcept { return m_den; }

    Rational operator+(const Rational& rhs) const {
        std::int64_t g = std::gcd(m_den, rhs.m_den);
        std::int64_t b_prime = m_den / g;
        std::int64_t d_prime = rhs.m_den / g;

        std::int64_t n = m_num * d_prime + rhs.m_num * b_prime;
        std::int64_t d = m_den * d_prime;
        return Rational(n, d);
    }

    Rational operator-(const Rational& rhs) const {
        return *this + Rational(-rhs.m_num, rhs.m_den);
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

    bool operator==(const Rational& rhs) const noexcept {
        return m_num == rhs.m_num && m_den == rhs.m_den;
    }

    std::string to_string() const {
        if (m_den == 1) return std::to_string(m_num);
        return std::to_string(m_num) + "/" + std::to_string(m_den);
    }
};

int main() {
    try {
        Rational a(7, 12);
        Rational b(5, 18);

        Rational sum = a + b;
        Rational prod = a * b;

        std::cout << "7/12 + 5/18 = " << sum.to_string() << "\n";
        std::cout << "7/12 * 5/18 = " << prod.to_string() << "\n";

    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
    }
    return 0;
}
