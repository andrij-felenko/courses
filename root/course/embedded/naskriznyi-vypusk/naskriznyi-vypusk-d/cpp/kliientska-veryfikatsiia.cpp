#include <cstdint>
#include <span>
#include <expected>
#include <array>

namespace release {

inline constexpr uint32_t SecureBootMagic = 0x53424F54;
inline constexpr uint32_t CurrentHwRevision = 0x0002; // Hardware Rev B

struct alignas(4) ImageHeader {
    uint32_t magic;
    uint32_t versionCode;
    uint32_t securityCounter;
    uint32_t hwCompatibilityMask;
    uint32_t payloadSize;
    std::array<uint8_t, 32> sha256Digest;
    std::array<uint8_t, 64> signature;
};

enum class VerifyError {
    BadMagic,
    HwIncompatible,
    RollbackDetected,
    ImageTooLarge,
    DigestMismatch
};

[[nodiscard]] std::expected<void, VerifyError> verifyReleaseHeader(
    const ImageHeader& hdr,
    uint32_t currentEfuseCounter,
    uint32_t maxFlashSize) noexcept {
    
    if (hdr.magic != SecureBootMagic) {
        return std::unexpected(VerifyError::BadMagic);
    }

    if ((hdr.hwCompatibilityMask & (1U << CurrentHwRevision)) == 0) {
        return std::unexpected(VerifyError::HwIncompatible);
    }

    if (hdr.securityCounter < currentEfuseCounter) {
        return std::unexpected(VerifyError::RollbackDetected);
    }

    if (hdr.payloadSize > maxFlashSize) {
        return std::unexpected(VerifyError::ImageTooLarge);
    }

    return {};
}

} // namespace release
