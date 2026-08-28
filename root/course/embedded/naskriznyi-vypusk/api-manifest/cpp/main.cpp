#include <cstdint>
#include <array>

namespace release {

inline constexpr size_t SecureBootHeaderSize = 128;
inline constexpr uint32_t SecureBootMagicValue = 0x53424F54;

struct alignas(4) SecureBootHeader {
    uint32_t magic;
    uint32_t versionPacked;
    uint32_t securityCounter;
    uint32_t hwMask;
    uint32_t payloadSize;
    std::array<uint8_t, 32> payloadDigest;
    std::array<uint8_t, 64> signature;
    std::array<uint8_t, 12> reserved;
};

static_assert(sizeof(SecureBootHeader) == SecureBootHeaderSize, "Header size must be 128 bytes");

} // namespace release
