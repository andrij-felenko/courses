#include <cstdint>
#include <span>
#include <expected>
#include <bit>

namespace iot::telemetry {

constexpr uint16_t MAGIC = 0xA55A;
constexpr uint8_t VERSION = 1;
constexpr size_t FRAME_SIZE = 24;

enum class ParseError {
    InvalidSize,
    InvalidMagic,
    UnsupportedVersion,
    ChecksumMismatch
};

struct Frame {
    uint32_t nodeId{0};
    uint32_t seqNum{0};
    uint32_t timestamp{0};
    float temperatureC{0.0f};
    float humidityPct{0.0f};
    float batteryV{0.0f};
    bool lowBattery{false};
    bool sensorFault{false};
    bool tamper{false};
    bool offlineSync{false};
};

[[nodiscard]] constexpr uint16_t calculateCrc16(std::span<const uint8_t> data) noexcept {
    uint16_t crc = 0xFFFF;
    for (uint8_t byte : data) {
        crc ^= static_cast<uint16_t>(byte) << 8;
        for (int i = 0; i < 8; ++i) {
            if (crc & 0x8000) {
                crc = static_cast<uint16_t>((crc << 1) ^ 0x1021);
            } else {
                crc = static_cast<uint16_t>(crc << 1);
            }
        }
    }
    return crc;
}

[[nodiscard]] inline std::expected<Frame, ParseError> parse(std::span<const uint8_t> buffer) noexcept {
    if (buffer.size() < FRAME_SIZE) {
        return std::unexpected(ParseError::InvalidSize);
    }

    const auto readU16 = [](const uint8_t* p) -> uint16_t {
        return static_cast<uint16_t>(p[0] | (p[1] << 8));
    };

    const auto readI16 = [](const uint8_t* p) -> int16_t {
        return static_cast<int16_t>(p[0] | (p[1] << 8));
    };

    const auto readU32 = [](const uint8_t* p) -> uint32_t {
        return static_cast<uint32_t>(p[0] | (p[1] << 8) | (p[2] << 16) | (p[3] << 24));
    };

    const uint16_t magic = readU16(&buffer[0]);
    if (magic != MAGIC) {
        return std::unexpected(ParseError::InvalidMagic);
    }

    const uint8_t version = buffer[2];
    if (version != VERSION) {
        return std::unexpected(ParseError::UnsupportedVersion);
    }

    const uint16_t expectedCrc = calculateCrc16(buffer.subspan(0, FRAME_SIZE - 2));
    const uint16_t actualCrc = readU16(&buffer[22]);
    if (expectedCrc != actualCrc) {
        return std::unexpected(ParseError::ChecksumMismatch);
    }

    Frame frame;
    const uint8_t flags = buffer[3];
    frame.nodeId = readU32(&buffer[4]);
    frame.seqNum = readU32(&buffer[8]);
    frame.timestamp = readU32(&buffer[12]);
    frame.temperatureC = static_cast<float>(readI16(&buffer[16])) / 100.0f;
    frame.humidityPct = static_cast<float>(readU16(&buffer[18])) / 100.0f;
    frame.batteryV = static_cast<float>(readU16(&buffer[20])) / 1000.0f;

    frame.lowBattery = (flags & (1 << 0)) != 0;
    frame.sensorFault = (flags & (1 << 1)) != 0;
    frame.tamper = (flags & (1 << 2)) != 0;
    frame.offlineSync = (flags & (1 << 3)) != 0;

    return frame;
}

} // namespace iot::telemetry
