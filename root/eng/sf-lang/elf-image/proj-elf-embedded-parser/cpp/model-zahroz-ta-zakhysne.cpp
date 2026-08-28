#include <cstdint>

namespace security {

inline constexpr std::uint32_t AppFlashStart = 0x08010000U;
inline constexpr std::uint32_t AppFlashEnd   = 0x080FFFFFU;

[[nodiscard]] constexpr bool is_valid_flash_destination(
    std::uint32_t paddr, std::uint32_t filesz) noexcept {
    if (paddr < AppFlashStart) return false;
    if (static_cast<std::uint64_t>(paddr) + filesz > AppFlashEnd + 1ULL) return false;
    return true;
}

} // namespace security
