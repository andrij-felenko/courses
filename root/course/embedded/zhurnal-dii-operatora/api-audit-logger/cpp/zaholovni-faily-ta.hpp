#pragma once

#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>
#include <string_view>

namespace embedded::audit {

inline constexpr size_t RecordSize = 128;
inline constexpr size_t HashSize = 32;
inline constexpr uint32_t MagicSync = 0x41554454;   // 'AUDT'
inline constexpr uint32_t SectorMagic = 0x53454354; // 'SECT'
inline constexpr size_t MaxPayloadSize = 32;

enum class Status : int32_t {
    Ok = 0,
    InvalidParam = -1,
    FlashIo = -2,
    ChainCorrupted = -3,
    BufferFull = -4,
    NotInitialized = -5,
    UnalignedAddr = -6,
    PowerLossDetected = -7
};

enum class ExecStatus : uint8_t {
    Pending = 0x00,
    Accepted = 0x01,
    RejectedAuth = 0x02,
    RejectedSafety = 0x03,
    Success = 0x04,
    Failed = 0x05,
    Timeout = 0x06
};

enum class RecordFlags : uint8_t {
    None = 0x00,
    Emergency = 0x01,
    SignatureValid = 0x02,
    SyncRtc = 0x08
};

inline constexpr RecordFlags operator|(RecordFlags a, RecordFlags b) noexcept {
    return static_cast<RecordFlags>(static_cast<uint8_t>(a) | static_cast<uint8_t>(b));
}

inline constexpr bool operator&(RecordFlags a, RecordFlags b) noexcept {
    return (static_cast<uint8_t>(a) & static_cast<uint8_t>(b)) != 0;
}

} // namespace embedded::audit
