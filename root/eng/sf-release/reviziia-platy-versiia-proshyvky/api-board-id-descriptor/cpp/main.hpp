#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <string_view>
#include <array>

namespace board::id {

inline constexpr uint32_t MagicHeader = 0x424F5244U;

enum class StatusCode : int8_t {
    Success = 0,
    I2cCommunicationFault = -1,
    InvalidMagicSignature = -2,
    ChecksumMismatch = -3,
    UnsupportedRevision = -4,
    CorruptedTlvStructure = -5
};

struct HardwareConfiguration {
    uint16_t hwRevision{0};
    uint16_t bomVariant{0};
    std::array<char, 17> serialNumber{};
    std::array<uint8_t, 6> macAddress{};
    uint16_t calibratedVrefMv{3300};
    std::array<int8_t, 9> imuOrientationMatrix{1, 0, 0, 0, 1, 0, 0, 0, 1};
};

/* Чистий функціональний інтерфейс парсера бінарного блоку TLV */
class DescriptorParser {
public:
    [[nodiscard]] static std::expected<HardwareConfiguration, StatusCode> 
    parseAndVerify(std::span<const uint8_t> rawEepromData) noexcept;

    [[nodiscard]] static constexpr uint16_t 
    calculateCrc16(std::span<const uint8_t> buffer) noexcept;
};

} // namespace board::id
