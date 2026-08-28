#include <iostream>
#include <array>
#include <cstdint>
#include <iomanip>

template <uint16_t Poly, uint8_t Bits>
class GaloisField {
public:
    static constexpr size_t Order = 1ULL << Bits;
    static constexpr size_t ModulusMask = Order - 1;

    // Побудова таблиць логарифмів та експонент під час компіляції (C++20 constexpr)
    struct Tables {
        std::array<uint8_t, Order> exp{};
        std::array<uint8_t, Order> log{};

        constexpr Tables() {
            uint8_t val = 1;
            for (size_t i = 0; i < Order - 1; ++i) {
                exp[i] = val;
                log[val] = static_cast<uint8_t>(i);
                
                // xtime множення
                uint16_t next = static_cast<uint16_t>(val << 1);
                if (next & Order) {
                    next ^= Poly;
                }
                val = static_cast<uint8_t>(next);
            }
            exp[Order - 1] = 1;
            log[0] = 0; // log(0) невизначений
        }
    };

    static constexpr Tables tables{};

    static constexpr uint8_t add(uint8_t a, uint8_t b) noexcept {
        return a ^ b;
    }

    static constexpr uint8_t mul(uint8_t a, uint8_t b) noexcept {
        if (a == 0 || b == 0) return 0;
        size_t sum_log = static_cast<size_t>(tables.log[a]) + tables.log[b];
        if (sum_log >= Order - 1) sum_log -= (Order - 1);
        return tables.exp[sum_log];
    }

    static constexpr uint8_t inv(uint8_t a) noexcept {
        if (a == 0) return 0;
        size_t log_inv = (Order - 1) - tables.log[a];
        return tables.exp[log_inv];
    }
};

using GF256 = GaloisField<0x11B, 8>; // Поле AES
using GF8   = GaloisField<0x0B, 3>;  // Поле GF(2^3)

// Генерація байта AES S-Box у сучасному C++
constexpr uint8_t aes_sbox(uint8_t input) noexcept {
    uint8_t inv = GF256::inv(input);
    uint8_t s = inv;
    s ^= static_cast<uint8_t>((inv << 1) | (inv >> 7));
    s ^= static_cast<uint8_t>((inv << 2) | (inv >> 6));
    s ^= static_cast<uint8_t>((inv << 3) | (inv >> 5));
    s ^= static_cast<uint8_t>((inv << 4) | (inv >> 4));
    return s ^ 0x63;
}

int main() {
    // Демонстрація табличного множення GF(2^3)
    uint8_t a8 = 5; // x^2 + 1
    uint8_t b8 = 3; // x + 1
    uint8_t c8 = GF8::mul(a8, b8);
    std::cout << "GF(2^3) C++: " << int(a8) << " * " << int(b8) << " = " 
              << int(c8) << " (очікується 4)\n";

    // Демонстрація AES GF(2^8)
    uint8_t a256 = 0x57;
    uint8_t b256 = 0x83;
    uint8_t c256 = GF256::mul(a256, b256);
    std::cout << "GF(2^8) AES C++: 0x" << std::hex << std::uppercase << int(a256)
              << " * 0x" << int(b256) << " = 0x" << int(c256) << " (очікується 0xC1)\n";

    uint8_t inv256 = GF256::inv(a256);
    uint8_t prod256 = GF256::mul(a256, inv256);
    std::cout << "GF(2^8) Inv C++: 0x" << int(a256) << "^(-1) = 0x" << int(inv256)
              << ", a * a^(-1) = 0x" << int(prod256) << "\n";

    std::cout << "AES S-Box C++: S(0x53) = 0x" << int(aes_sbox(0x53)) << " (очікується 0xED)\n";

    return 0;
}
