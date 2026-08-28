/* Типобезпечний C++ підхід з constexpr бітовими помічниками */
#include <cstdint>
#include <cstddef>

namespace driver {

namespace ctrl_bits {
    inline constexpr uint8_t OdrPos   = 4;
    inline constexpr uint8_t OdrMask  = 0x07 << OdrPos;
    inline constexpr uint8_t Odr100Hz = 0x03 << OdrPos;
    inline constexpr uint8_t BduBit   = 1 << 3;
    inline constexpr uint8_t EnableBit = 1 << 0;
}

[[nodiscard]] constexpr uint8_t configure_register(uint8_t current_val) noexcept {
    using namespace ctrl_bits;
    auto val = static_cast<uint8_t>(current_val & ~OdrMask);
    val |= Odr100Hz | BduBit | EnableBit;
    return val;
}

} // namespace driver
