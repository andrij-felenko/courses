#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>

namespace emergency {

inline constexpr uint32_t HeaderMagic = 0x454D4759U; // 'EMGY'
inline constexpr uint16_t CurrentHeaderVersion = 1U;
inline constexpr size_t SignatureSizeBytes = 64U;
inline constexpr size_t Sha256SizeBytes = 32U;
inline constexpr size_t HeaderTotalSizeBytes = 256U;

enum class Flag : uint32_t {
    CriticalCvss  = (1U << 0),
    ForceApply    = (1U << 1),
    BurnRollback  = (1U << 2),
    CanaryTested  = (1U << 3),
    DualCoreSync  = (1U << 4),
};

enum class CoreId : uint16_t {
    MainApplication = 0,
    RadioCoprocessor = 1,
};

#pragma pack(push, 1)
struct Header {
    uint32_t magic{HeaderMagic};
    uint16_t headerVersion{CurrentHeaderVersion};
    uint16_t headerSize{static_cast<uint16_t>(HeaderTotalSizeBytes)};
    
    uint8_t  verMajor{0};
    uint8_t  verMinor{0};
    uint16_t verPatch{0};
    uint8_t  buildType{0};
    uint32_t commitHashPrefix{0};
    
    uint32_t targetHwId{0};
    uint16_t minHwRev{0};
    uint16_t maxHwRev{0};
    CoreId   targetCoreId{CoreId::MainApplication};
    
    uint32_t securityCounter{0};
    uint32_t flags{0};
    
    uint32_t payloadOffset{0};
    uint32_t payloadSize{0};
    uint32_t payloadEntryPoint{0};
    uint32_t payloadCrc32{0};
    
    uint8_t  payloadSha256[Sha256SizeBytes]{};
    uint8_t  headerSignature[SignatureSizeBytes]{};
    
    uint8_t  reserved[74]{};
    
    [[nodiscard]] constexpr bool hasFlag(Flag flag) const noexcept {
        return (flags & static_cast<uint32_t>(flag)) != 0;
    }
};
#pragma pack(pop)

static_assert(sizeof(Header) == HeaderTotalSizeBytes, "Header size must strictly be 256 bytes");

enum class ValidationError : int32_t {
    BadMagic            = -1,
    UnsupportedVersion  = -2,
    HardwareMismatch    = -3,
    CoreMismatch        = -4,
    RollbackBlocked     = -5,
    PayloadBounds       = -6,
    CrcMismatch         = -7,
    HashMismatch        = -8,
    SignatureInvalid    = -9,
    FlashWriteFailure   = -10
};

} // namespace emergency
