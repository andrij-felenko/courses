#include <cstdint>
#include <optional>

namespace trng {

[[nodiscard]] constexpr std::optional<uint8_t> von_neumann_extract(uint8_t b1, uint8_t b2) noexcept {
    if (b1 == 0 && b2 == 1) {
        return 0;
    }
    if (b1 == 1 && b2 == 0) {
        return 1;
    }
    return std::nullopt; // 00 або 11 — відкидання
}

} // namespace trng
