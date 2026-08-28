/* C++ constexpr реалізація знакового розширення довільної розрядності */
#include <cstdint>
#include <concepts>

namespace driver {

template <size_t Bits>
requires (Bits > 0 && Bits < 16)
[[nodiscard]] constexpr int16_t sign_extend(uint16_t raw) noexcept {
    constexpr uint16_t SignMask = 1U << (Bits - 1);
    constexpr uint16_t FillMask = ~((1U << Bits) - 1U);
    
    if ((raw & SignMask) != 0) {
        return static_cast<int16_t>(raw | FillMask);
    }
    return static_cast<int16_t>(raw & ~FillMask);
}

} // namespace driver
