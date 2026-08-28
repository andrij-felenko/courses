// Ідіоматичний C++20 модуль серіалізації телеметрії
#include <array>
#include <span>
#include <string_view>
#include <cstdint>
#include <expected>
#include <bit>
#include <cstring>
#include <cstdio>

enum class FramingError {
    BufferTooSmall,
    FormattingError,
    InvalidCrc,
    InvalidMagic
};

struct TelemetrySample {
    std::uint32_t timestamp_s{0};
    std::int16_t  temp_centi_c{0};
    std::uint16_t humidity_pct{0};
    std::uint16_t vbat_mv{0};
};

class ProtocolSerializer {
public:
    // 1. Формування HTTP POST (C++20 string_view та без динамічної пам'яті)
    [[nodiscard]] static std::expected<std::size_t, FramingError>
    buildHttpPost(const TelemetrySample& s,
                  std::string_view host,
                  std::string_view token,
                  std::span<char> out_buf) noexcept
    {
        char json_buf[96];
        const double temp = static_cast<double>(s.temp_centi_c) / 100.0;
        const double hum = static_cast<double>(s.humidity_pct) / 100.0;

        const int json_len = std::snprintf(json_buf, sizeof(json_buf),
            R"({{"ts":%lu,"t":%.2f,"h":%.2f,"vbat":%u}})",
            static_cast<unsigned long>(s.timestamp_s), temp, hum, s.vbat_mv);

        if (json_len < 0 || static_cast<std::size_t>(json_len) >= sizeof(json_buf)) {
            return std::unexpected(FramingError::FormattingError);
        }

        const int total_len = std::snprintf(out_buf.data(), out_buf.size(),
            "POST /api/v1/telemetry HTTP/1.1\r\n"
            "Host: %.*s\r\n"
            "Authorization: Bearer %.*s\r\n"
            "Content-Type: application/json\r\n"
            "Content-Length: %d\r\n"
            "Connection: close\r\n\r\n%.*s",
            static_cast<int>(host.size()), host.data(),
            static_cast<int>(token.size()), token.data(),
            json_len, json_len, json_buf);

        if (total_len < 0 || static_cast<std::size_t>(total_len) >= out_buf.size()) {
            return std::unexpected(FramingError::BufferTooSmall);
        }

        return static_cast<std::size_t>(total_len);
    }

    // 2. Формування MQTT PUBLISH (QoS 1)
    [[nodiscard]] static std::expected<std::size_t, FramingError>
    buildMqttPublishQos1(const TelemetrySample& s,
                         std::string_view topic,
                         std::uint16_t packet_id,
                         std::span<std::uint8_t> out_buf) noexcept
    {
        char payload[48];
        const int plen = std::snprintf(payload, sizeof(payload),
            R"({{"t":%d,"h":%u,"v":%u}})",
            s.temp_centi_c, s.humidity_pct, s.vbat_mv);

        if (plen < 0) return std::unexpected(FramingError::FormattingError);

        const std::size_t var_hdr_len = 2 + topic.size() + 2;
        const std::size_t remaining_len = var_hdr_len + static_cast<std::size_t>(plen);

        if (remaining_len > 127 || (2 + remaining_len) > out_buf.size()) {
            return std::unexpected(FramingError::BufferTooSmall);
        }

        std::size_t idx = 0;
        out_buf[idx++] = 0x32; // PUBLISH, QoS 1
        out_buf[idx++] = static_cast<std::uint8_t>(remaining_len);

        // Topic length (Big Endian)
        out_buf[idx++] = static_cast<std::uint8_t>(topic.size() >> 8);
        out_buf[idx++] = static_cast<std::uint8_t>(topic.size() & 0xFF);
        std::memcpy(&out_buf[idx], topic.data(), topic.size());
        idx += topic.size();

        // Packet ID
        out_buf[idx++] = static_cast<std::uint8_t>(packet_id >> 8);
        out_buf[idx++] = static_cast<std::uint8_t>(packet_id & 0xFF);

        // Payload
        std::memcpy(&out_buf[idx], payload, plen);
        idx += plen;

        return idx;
    }

    // 3. Власний бінарний кадр
    struct alignas(1) BinaryFrame {
        std::uint8_t  magic{0xAA};
        std::uint8_t  msg_type{0x01};
        std::uint16_t seq_num{0};
        std::uint32_t timestamp_s{0};
        std::int16_t  temp_c{0};
        std::uint16_t hum_pct{0};
        std::uint16_t vbat_mv{0};
        std::uint16_t crc16{0};
    };

    [[nodiscard]] static std::expected<std::size_t, FramingError>
    buildBinaryFrame(const TelemetrySample& s,
                     std::uint16_t seq,
                     std::span<std::uint8_t> out_buf) noexcept
    {
        if (out_buf.size() < sizeof(BinaryFrame)) {
            return std::unexpected(FramingError::BufferTooSmall);
        }

        BinaryFrame frame{
            .magic = 0xAA,
            .msg_type = 0x01,
            .seq_num = seq,
            .timestamp_s = s.timestamp_s,
            .temp_c = s.temp_centi_c,
            .hum_pct = s.humidity_pct,
            .vbat_mv = s.vbat_mv,
            .crc16 = 0
        };

        const auto* raw_ptr = reinterpret_cast<const std::uint8_t*>(&frame);
        constexpr std::size_t check_len = sizeof(BinaryFrame) - sizeof(std::uint16_t);
        frame.crc16 = calculateCrc16({raw_ptr, check_len});

        std::memcpy(out_buf.data(), &frame, sizeof(BinaryFrame));
        return sizeof(BinaryFrame);
    }

private:
    [[nodiscard]] static constexpr std::uint16_t
    calculateCrc16(std::span<const std::uint8_t> data) noexcept {
        std::uint16_t crc = 0xFFFF;
        for (const auto b : data) {
            crc ^= static_cast<std::uint16_t>(b) << 8;
            for (int i = 0; i < 8; ++i) {
                if ((crc & 0x8000) != 0) {
                    crc = (crc << 1) ^ 0x1021;
                } else {
                    crc = crc << 1;
                }
            }
        }
        return crc;
    }
};
