#include <iostream>
#include <array>
#include <cstdint>
#include <span>
#include <optional>
#include <stdexcept>

namespace galois {

/**
 * @brief Ідіоматичний C++20 клас для виконання арифметики у полі GF(2^8) AES
 */
class GaloisField256 {
public:
    static constexpr uint16_t AES_POLYNOMIAL = 0x11B;
    static constexpr size_t ORDER = 256;

    constexpr GaloisField256() noexcept {
        init_tables();
    }

    [[nodiscard]] constexpr uint8_t add(uint8_t a, uint8_t b) const noexcept {
        return a ^ b;
    }

    [[nodiscard]] constexpr uint8_t subtract(uint8_t a, uint8_t b) const noexcept {
        return a ^ b;
    }

    [[nodiscard]] constexpr uint8_t mul_x(uint8_t a) const noexcept {
        return (a & 0x80) ? static_cast<uint8_t>((a << 1) ^ 0x1B) 
                          : static_cast<uint8_t>(a << 1);
    }

    [[nodiscard]] constexpr uint8_t multiply_slow(uint8_t a, uint8_t b) const noexcept {
        uint8_t res = 0;
        uint8_t cur_a = a;
        uint8_t cur_b = b;

        while (cur_b > 0) {
            if (cur_b & 1) {
                res ^= cur_a;
            }
            cur_a = mul_x(cur_a);
            cur_b >>= 1;
        }
        return res;
    }

    [[nodiscard]] uint8_t multiply(uint8_t a, uint8_t b) const noexcept {
        if (a == 0 || b == 0) return 0;
        const size_t log_sum = static_cast<size_t>(log_table_[a]) + log_table_[b];
        return exp_table_[log_sum];
    }

    [[nodiscard]] std::optional<uint8_t> divide(uint8_t a, uint8_t b) const noexcept {
        if (b == 0) return std::nullopt;
        if (a == 0) return 0;
        const int log_diff = static_cast<int>(log_table_[a]) - static_cast<int>(log_table_[b]) + 255;
        return exp_table_[static_cast<size_t>(log_diff % 255)];
    }

    [[nodiscard]] const std::array<uint8_t, ORDER>& get_log_table() const noexcept {
        return log_table_;
    }

    [[nodiscard]] const std::array<uint8_t, ORDER * 2>& get_exp_table() const noexcept {
        return exp_table_;
    }

private:
    std::array<uint8_t, ORDER * 2> exp_table_{};
    std::array<uint8_t, ORDER> log_table_{};

    constexpr void init_tables() noexcept {
        uint8_t val = 1;
        constexpr uint8_t primitive = 0x03;

        for (size_t i = 0; i < 255; ++i) {
            exp_table_[i] = val;
            exp_table_[i + 255] = val;
            log_table_[val] = static_cast<uint8_t>(i);
            val = multiply_slow(val, primitive);
        }
        log_table_[0] = 0;
    }
};

} // namespace galois
