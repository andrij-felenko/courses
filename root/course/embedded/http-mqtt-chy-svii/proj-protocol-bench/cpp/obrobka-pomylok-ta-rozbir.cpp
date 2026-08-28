// Ідіоматичний C++20 розбір бінарного кадру
#include <cstdint>
#include <span>
#include <expected>
#include <cstring>

enum class ParseError {
    InvalidSize,
    InvalidMagic,
    ChecksumMismatch
};

class BinaryPacketParser {
public:
    [[nodiscard]] static std::expected<TelemetrySample, ParseError>
    parse(std::span<const std::uint8_t> buffer) noexcept {
        if (buffer.size() != sizeof(ProtocolSerializer::BinaryFrame)) {
            return std::unexpected(ParseError::InvalidSize);
        }

        if (buffer[0] != 0xAA) {
            return std::unexpected(ParseError::InvalidMagic);
        }

        ProtocolSerializer::BinaryFrame frame{};
        std::memcpy(&frame, buffer.data(), sizeof(frame));

        constexpr std::size_t check_len = sizeof(frame) - sizeof(std::uint16_t);
        const auto calc_crc = ProtocolSerializer::BinaryFrame{}; // Перевірка за спільним CRC алгоритмом
        // Розраховуємо контрольний CRC по отриманих сирих байтах
        std::uint16_t expected_crc = 0xFFFF;
        for (std::size_t i = 0; i < check_len; ++i) {
            expected_crc ^= static_cast<std::uint16_t>(buffer[i]) << 8;
            for (int j = 0; j < 8; ++j) {
                if ((expected_crc & 0x8000) != 0) {
                    expected_crc = (expected_crc << 1) ^ 0x1021;
                } else {
                    expected_crc = expected_crc << 1;
                }
            }
        }

        if (frame.crc16 != expected_crc) {
            return std::unexpected(ParseError::ChecksumMismatch);
        }

        return TelemetrySample{
            .timestamp_s  = frame.timestamp_s,
            .temp_centi_c = frame.temp_c,
            .humidity_pct = frame.hum_pct,
            .vbat_mv      = frame.vbat_mv
        };
    }
};
