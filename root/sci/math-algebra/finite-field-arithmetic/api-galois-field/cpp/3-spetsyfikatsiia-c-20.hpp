#ifndef GALOIS_FIELD_HPP
#define GALOIS_FIELD_HPP

#include <array>
#include <cstdint>
#include <optional>
#include <type_traits>
#include <concepts>

namespace galois {

template <typename T>
concept UnsignedInteger = std::is_unsigned_v<T> && !std::is_same_v<T, bool>;

template <UnsignedInteger T, size_t m, T IrreduciblePolynomial>
class Field {
public:
    static_assert(m > 0 && m <= sizeof(T) * 8, "Степінь m повинна відповідати розміру типу T");

    using value_type = T;

    constexpr Field() noexcept = default;

    [[nodiscard]] constexpr T add(T a, T b) const noexcept {
        return a ^ b;
    }

    [[nodiscard]] constexpr T subtract(T a, T b) const noexcept {
        return a ^ b;
    }

    [[nodiscard]] constexpr T multiply_constant_time(T a, T b) const noexcept {
        T res = 0;
        T cur_a = a;
        T cur_b = b;
        const T poly_lower = IrreduciblePolynomial & ((static_cast<T>(1) << m) - 1);

        for (size_t i = 0; i < m; ++i) {
            T mask = static_cast<T>(0) - (cur_b & 1);
            res ^= (cur_a & mask);
            T carry = static_cast<T>(0) - ((cur_a >> (m - 1)) & 1);
            cur_a = static_cast<T>(cur_a << 1) ^ (poly_lower & carry);
            cur_b = static_cast<T>(cur_b >> 1);
        }
        return res;
    }

    [[nodiscard]] constexpr std::optional<T> inverse_fermat(T a) const noexcept {
        if (a == 0) return std::nullopt;
        T result = 1;
        T base = a;
        uint64_t exponent = (1ULL << m) - 2;

        while (exponent > 0) {
            if (exponent & 1) {
                result = multiply_constant_time(result, base);
            }
            base = multiply_constant_time(base, base);
            exponent >>= 1;
        }
        return result;
    }
};

using GF256_AES = Field<uint8_t, 8, 0x11B>;
using GF64_CRCPOLY = Field<uint64_t, 64, 0x1BULL>;

} // namespace galois

#endif // GALOIS_FIELD_HPP
