#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>
#include <algorithm>

inline constexpr std::size_t OemKeySlots = 4;
inline constexpr std::size_t Sha256DigestSize = 32;
inline constexpr std::size_t SignatureSize = 64;
inline constexpr std::size_t PublicKeySize = 64;
inline constexpr std::uint32_t FwMagic = 0x53454355; // "SECU"

enum class BootError : std::uint8_t {
    InvalidMagic,
    KeySlotOutOfBounds,
    KeyRevoked,
    KeyHashMismatch,
    VersionRollback,
    PayloadCorrupted,
    SignatureInvalid,
    EfuseBurnFailed
};

#pragma pack(push, 1)
struct FirmwareHeader {
    std::uint32_t magic;
    std::uint32_t fw_version;
    std::uint32_t key_slot_index;
    std::uint32_t payload_length;
    std::array<std::uint8_t, PublicKeySize> public_key;
    std::array<std::uint8_t, SignatureSize> signature;
    std::array<std::uint8_t, Sha256DigestSize> payload_sha256;
};
#pragma pack(pop)

struct HardwareEfuseBank {
    std::array<std::array<std::uint8_t, Sha256DigestSize>, OemKeySlots> root_key_hashes;
    std::uint32_t revoked_keys_mask{0};
    std::uint32_t monotonic_version{0};
    bool security_locked{true};
};
