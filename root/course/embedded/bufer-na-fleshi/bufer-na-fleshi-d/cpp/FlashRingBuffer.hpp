// FlashRingBuffer.hpp
#pragma once

#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>
#include <concepts>

namespace embedded::storage {

inline constexpr uint32_t FlashSectorSize    = 4096U;
inline constexpr uint32_t FlashSectorMagic   = 0x53454354U; // ASCII "SECT"
inline constexpr uint16_t FlashRecordMagic   = 0x5243U;     // ASCII "RC"

enum class RecordStatus : uint8_t {
    Free      = 0xFFU,
    Writing   = 0xFEU,
    Committed = 0xFCU,
    Consumed  = 0x00U
};

enum class RingError {
    Full,
    Empty,
    Corrupted,
    IoError,
    InvalidParameter
};

struct SectorHeader {
    uint32_t               magic{FlashSectorMagic};
    uint32_t               sector_seq{0};
    uint8_t                state_flag{static_cast<uint8_t>(RecordStatus::Free)};
    std::array<uint8_t, 3> reserved{0, 0, 0};
    uint32_t               header_crc32{0};
} __attribute__((packed));

struct RecordHeader {
    uint16_t record_magic{FlashRecordMagic};
    uint16_t payload_len{0};
    uint32_t record_seq{0};
    uint8_t  status_flag{static_cast<uint8_t>(RecordStatus::Free)};
    uint8_t  priority{0};
    uint16_t reserved{0};
    uint32_t payload_crc32{0};
} __attribute__((packed));

// Концепт для апаратного драйвера SPI Flash
template <typename T>
concept FlashDriver = requires(T driver, uint32_t addr, const uint8_t* src, uint8_t* dst, size_t len) {
    { driver.read(addr, dst, len) } -> std::same_as<int>;
    { driver.write_page(addr, src, len) } -> std::same_as<int>;
    { driver.erase_sector(addr) } -> std::same_as<int>;
};

} // namespace embedded::storage
