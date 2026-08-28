#include <cstdint>
#include <array>
#include <cstddef>

namespace firmware_format {

constexpr uint32_t MagicValue = 0x5346574D; // "SFWM"
constexpr uint16_t HeaderVersion2 = 0x0002;
constexpr size_t HeaderSizeBytes = 64;

enum class ImageFlags : uint16_t {
    None           = 0x0000,
    Encrypted      = 0x0001,
    BridgeImage    = 0x0002,
    CommitRotation = 0x0004,
    DualSigned     = 0x0008
};

enum class CryptoSuite : uint8_t {
    Ed25519Sha256   = 0x01,
    EcdsaP256Sha256 = 0x02,
    Rsa3072PssSha256= 0x03,
    Rsa4096Sha384   = 0x04
};

#pragma pack(push, 1)
struct FirmwareEnvelopeHeader {
    uint32_t magic;
    uint16_t headerVersion;
    uint16_t flags;
    uint32_t headerSize;
    uint32_t payloadSize;
    uint32_t securityVersion;
    uint32_t targetHardwareId;
    CryptoSuite cryptoSuite;
    uint8_t  keySlotIndex;
    uint16_t certChainLength;
    std::array<uint8_t, 32> payloadHash;
    uint32_t headerCrc32;
};
#pragma pack(pop)

static_assert(sizeof(FirmwareEnvelopeHeader) == HeaderSizeBytes, "FirmwareEnvelopeHeader must be exactly 64 bytes");

} // namespace firmware_format
