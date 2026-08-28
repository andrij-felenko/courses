#include <cstdint>

namespace mcuboot {

enum class ImageFlags : uint32_t {
    None             = 0,
    EncryptedAes128  = 0x00000004U,
    EncryptedAes256  = 0x00000008U,
    NonBootable      = 0x00000010U,
    RamLoad          = 0x00000020U,
    EncryptedEc256   = 0x00000040U,
    EncryptedX25519  = 0x00000080U
};

[[nodiscard]] constexpr bool has_flag(uint32_t mask, ImageFlags flag) noexcept {
    return (mask & static_cast<uint32_t>(flag)) != 0;
}

} // namespace mcuboot
