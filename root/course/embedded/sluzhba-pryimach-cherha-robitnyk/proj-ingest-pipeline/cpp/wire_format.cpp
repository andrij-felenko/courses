#include "wire_format.hpp"

#include <cstdio>

namespace ingest {
namespace {

// Розкладка кадру (зміщення в байтах):
//   0..1  magic 0xAA55      12..13 raw_temp   int16, крок 0.01 °C
//   2     version           14..15 raw_hum    uint16, крок 0.01 %
//   3     flags             16..17 raw_vbat   uint16, крок 0.001 В
//   4..7  device_id  uint32 18..19 seq        uint16
//   8..11 uptime_ms  uint32 20..21 status     uint16
//                          22..23 crc16 по байтах 0..21
std::uint16_t rd16(std::span<const std::uint8_t> b, std::size_t off) noexcept {
    return static_cast<std::uint16_t>((static_cast<std::uint16_t>(b[off]) << 8) | b[off + 1]);
}

std::uint32_t rd32(std::span<const std::uint8_t> b, std::size_t off) noexcept {
    return (static_cast<std::uint32_t>(b[off]) << 24) |
           (static_cast<std::uint32_t>(b[off + 1]) << 16) |
           (static_cast<std::uint32_t>(b[off + 2]) << 8) |
           static_cast<std::uint32_t>(b[off + 3]);
}

void wr16(std::vector<std::uint8_t>& b, std::size_t off, std::uint16_t v) noexcept {
    b[off] = static_cast<std::uint8_t>(v >> 8);
    b[off + 1] = static_cast<std::uint8_t>(v & 0xFF);
}

void wr32(std::vector<std::uint8_t>& b, std::size_t off, std::uint32_t v) noexcept {
    b[off] = static_cast<std::uint8_t>(v >> 24);
    b[off + 1] = static_cast<std::uint8_t>((v >> 16) & 0xFF);
    b[off + 2] = static_cast<std::uint8_t>((v >> 8) & 0xFF);
    b[off + 3] = static_cast<std::uint8_t>(v & 0xFF);
}

}  // namespace

const char* to_string(FrameError error) noexcept {
    switch (error) {
        case FrameError::none: return "none";
        case FrameError::bad_size: return "bad_size";
        case FrameError::bad_magic: return "bad_magic";
        case FrameError::bad_version: return "bad_version";
        case FrameError::crc_mismatch: return "crc_mismatch";
    }
    return "unknown";
}

// Побітовий CRC-16/CCITT (поліном 0x1021, початкове 0xFFFF), без таблиці й без алокацій:
// 24 байти на кадр — таблиця тут не окупається, а кеш економиться.
std::uint16_t crc16_ccitt(std::span<const std::uint8_t> bytes) noexcept {
    std::uint16_t crc = 0xFFFF;
    for (std::uint8_t byte : bytes) {
        crc ^= static_cast<std::uint16_t>(byte) << 8;
        for (int bit = 0; bit < 8; ++bit) {
            crc = (crc & 0x8000) ? static_cast<std::uint16_t>((crc << 1) ^ 0x1021)
                                 : static_cast<std::uint16_t>(crc << 1);
        }
    }
    return crc;
}

DecodeResult decode_frame(std::span<const std::uint8_t> bytes) noexcept {
    DecodeResult result;

    if (bytes.size() != kFrameSize) {
        result.error = FrameError::bad_size;
        return result;
    }
    if (rd16(bytes, 0) != kMagic) {
        result.error = FrameError::bad_magic;
        return result;
    }
    if (bytes[2] != kVersion) {
        result.error = FrameError::bad_version;
        return result;
    }

    // CRC рахуємо по всьому, крім самих двох байтів CRC.
    if (rd16(bytes, 22) != crc16_ccitt(bytes.first(22))) {
        result.error = FrameError::crc_mismatch;
        return result;
    }

    TelemetryFrame& frame = result.frame;
    frame.device_id = rd32(bytes, 4);
    frame.uptime_ms = rd32(bytes, 8);
    frame.temperature_c = static_cast<std::int16_t>(rd16(bytes, 12)) * 0.01;
    frame.humidity_pct = rd16(bytes, 14) * 0.01;
    frame.battery_v = rd16(bytes, 16) * 0.001;
    frame.seq = rd16(bytes, 18);
    frame.status = rd16(bytes, 20);
    return result;
}

bool in_physical_range(const TelemetryFrame& frame) noexcept {
    return frame.temperature_c >= -40.0 && frame.temperature_c <= 125.0 &&
           frame.humidity_pct >= 0.0 && frame.humidity_pct <= 100.0 &&
           frame.battery_v >= 2.5 && frame.battery_v <= 4.6;
}

std::string format_device_id(std::uint32_t raw_id) {
    char buffer[24];
    std::snprintf(buffer, sizeof(buffer), "esp32-%08x", raw_id);
    return std::string(buffer);
}

std::vector<std::uint8_t> encode_frame(std::uint32_t device_id, std::uint32_t uptime_ms,
                                       std::int16_t raw_temp, std::uint16_t raw_humidity,
                                       std::uint16_t raw_battery, std::uint16_t seq,
                                       std::uint16_t status) {
    std::vector<std::uint8_t> frame(kFrameSize, 0);
    wr16(frame, 0, kMagic);
    frame[2] = kVersion;
    frame[3] = 0x00;  // flags
    wr32(frame, 4, device_id);
    wr32(frame, 8, uptime_ms);
    wr16(frame, 12, static_cast<std::uint16_t>(raw_temp));
    wr16(frame, 14, raw_humidity);
    wr16(frame, 16, raw_battery);
    wr16(frame, 18, seq);
    wr16(frame, 20, status);
    wr16(frame, 22, crc16_ccitt(std::span<const std::uint8_t>(frame).first(22)));
    return frame;
}

}  // namespace ingest
