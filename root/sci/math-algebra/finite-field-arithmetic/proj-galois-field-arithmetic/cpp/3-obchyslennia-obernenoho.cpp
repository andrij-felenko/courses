#include <cstdint>
#include <optional>
#include <utility>

namespace galois {

/**
 * @brief Обчислення мультиплікативно оберненого елемента у GF(2^8) за допомогою Евкліда
 * @param a Вхідний ненульовий елемент
 * @return std::optional<uint8_t> Обернений елемент або std::nullopt для 0
 */
[[nodiscard]] constexpr std::optional<uint8_t> gf_inverse(uint8_t a) noexcept {
    if (a == 0) return std::nullopt;

    auto poly_deg = [](uint32_t p) noexcept -> int {
        int deg = -1;
        while (p > 0) {
            deg++;
            p >>= 1;
        }
        return deg;
    };

    uint32_t r0 = 0x11B; // Незвідний багаточлен AES
    uint32_t r1 = a;
    uint32_t v0 = 0;
    uint32_t v1 = 1;

    while (r1 > 1) {
        int deg0 = poly_deg(r0);
        int deg1 = poly_deg(r1);
        int shift = deg0 - deg1;

        if (shift < 0) {
            std::swap(r0, r1);
            std::swap(v0, v1);
            shift = -shift;
        }

        r0 ^= (r1 << shift);
        v0 ^= (v1 << shift);
    }

    return static_cast<uint8_t>(v1);
}

} // namespace galois
