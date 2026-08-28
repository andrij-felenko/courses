#include <cstdint>
#include <concepts>
#include <iostream>
#include <optional>
#include <vector>
#include <utility>
#include <stdexcept>

template <std::integral T = int64_t>
class GaussianInteger {
public:
    T re{0};
    T im{0};

    constexpr GaussianInteger() noexcept = default;
    constexpr GaussianInteger(T r, T i) noexcept : re(r), im(i) {}

    /* Базові арифметичні оператори */
    constexpr GaussianInteger operator+(const GaussianInteger& o) const noexcept {
        return {re + o.re, im + o.im};
    }

    constexpr GaussianInteger operator-(const GaussianInteger& o) const noexcept {
        return {re - o.re, im - o.im};
    }

    constexpr GaussianInteger operator*(const GaussianInteger& o) const noexcept {
        return {re * o.re - im * o.im, re * o.im + im * o.re};
    }

    constexpr GaussianInteger operator-() const noexcept {
        return {-re, -im};
    }

    constexpr bool operator==(const GaussianInteger& o) const noexcept = default;

    /* Комплексне спряження */
    [[nodiscard]] constexpr GaussianInteger conj() const noexcept {
        return {re, -im};
    }

    /* Алгебраїчна норма N(z) = re^2 + im^2 */
    [[nodiscard]] constexpr uint64_t norm() const noexcept {
        return static_cast<uint64_t>(re) * static_cast<uint64_t>(re) +
               static_cast<uint64_t>(im) * static_cast<uint64_t>(im);
    }

    [[nodiscard]] constexpr bool is_zero() const noexcept {
        return re == 0 && im == 0;
    }

    [[nodiscard]] constexpr bool is_unit() const noexcept {
        return norm() == 1;
    }
};

template <std::integral T>
std::ostream& operator<<(std::ostream& os, const GaussianInteger<T>& z) {
    os << z.re;
    if (z.im >= 0) os << " + " << z.im << "i";
    else os << " - " << -z.im << "i";
    return os;
}
