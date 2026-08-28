#include <cstdint>
#include <span>
#include <expected>
#include <array>

namespace release {

inline constexpr uint32_t SecureBootMagic = 0x53424F54;
inline constexpr uint32_t CurrentHardwareMask = 0x0002;

struct alignas(4) ReleaseHeader {
    uint32_t magic;
    uint32_t versionPacked;
    uint32_t securityCounter;
    uint32_t hwMask;
    uint32_t payloadSize;
    std::array<uint8_t, 32> payloadSha256;
    std::array<uint8_t, 64> signature;
    std::array<uint8_t, 12> reserved;
};

enum class ParseError {
    BufferOverflow,
    InvalidMagic,
    IncompatibleHardware,
    AntiRollbackViolation
};

[[nodiscard]] std::expected<void, ParseError> validateImageHeader(
    std::span<const uint8_t> headerBytes,
    uint32_t activeSecurityCounter,
    uint32_t maxAllowedSize) noexcept {
    
    if (headerBytes.size() < sizeof(ReleaseHeader)) {
        return std::unexpected(ParseError::BufferOverflow);
    }

    const auto* hdr = reinterpret_cast<const ReleaseHeader*>(headerBytes.data());

    if (hdr->magic != SecureBootMagic) {
        return std::unexpected(ParseError::InvalidMagic);
    }

    if ((hdr->hwMask & CurrentHardwareMask) == 0) {
        return std::unexpected(ParseError::IncompatibleHardware);
    }

    if (hdr->securityCounter < activeSecurityCounter) {
        return std::unexpected(ParseError::AntiRollbackViolation);
    }

    if (hdr->payloadSize > maxAllowedSize) {
        return std::unexpected(ParseError::BufferOverflow);
    }

    return {};
}

} // namespace release
