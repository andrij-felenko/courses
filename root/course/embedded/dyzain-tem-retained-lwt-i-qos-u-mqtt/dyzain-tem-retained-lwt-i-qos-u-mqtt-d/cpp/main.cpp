#include <array>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <optional>
#include <span>
#include <string_view>

namespace embedded::mqtt {

enum class PacketType : uint8_t {
    Connect = 0x10,
    Publish = 0x30
};

enum class QoS : uint8_t {
    AtMostOnce  = 0,
    AtLeastOnce = 1,
    ExactlyOnce = 2
};

struct WillMessage {
    std::string_view topic;
    std::string_view message;
    QoS              qos{QoS::AtLeastOnce};
    bool             retain{true};
};

struct ConnectOptions {
    std::string_view             client_id;
    uint16_t                     keep_alive_sec{60};
    bool                         clean_session{true};
    std::optional<WillMessage>   will{std::nullopt};
};

class PacketBuilder {
public:
    static std::span<uint8_t> pack_connect(std::span<uint8_t> buffer,
                                           const ConnectOptions& options) noexcept {
        if (options.client_id.empty() || buffer.size() < 64) {
            return {};
        }

        std::array<uint8_t, 256> payload_buf{};
        size_t payload_len = 0;

        uint8_t flags = 0;
        if (options.clean_session) flags |= 0x02;

        payload_len += write_string(std::span(payload_buf).subspan(payload_len), options.client_id);

        if (options.will.has_value()) {
            flags |= 0x04;
            flags |= (static_cast<uint8_t>(options.will->qos) & 0x03) << 3;
            if (options.will->retain) flags |= 0x20;

            payload_len += write_string(std::span(payload_buf).subspan(payload_len), options.will->topic);
            payload_len += write_string(std::span(payload_buf).subspan(payload_len), options.will->message);
        }

        const std::array<uint8_t, 10> var_header{
            0x00, 0x04, 'M', 'Q', 'T', 'T', 0x04,
            flags,
            static_cast<uint8_t>((options.keep_alive_sec >> 8) & 0xFF),
            static_cast<uint8_t>(options.keep_alive_sec & 0xFF)
        };

        const size_t rem_len = var_header.size() + payload_len;
        std::array<uint8_t, 4> rem_len_buf{};
        const size_t rem_len_bytes = encode_remaining_length(rem_len_buf, rem_len);

        const size_t total_size = 1 + rem_len_bytes + rem_len;
        if (total_size > buffer.size()) {
            return {};
        }

        buffer[0] = static_cast<uint8_t>(PacketType::Connect);
        std::memcpy(&buffer[1], rem_len_buf.data(), rem_len_bytes);
        std::memcpy(&buffer[1 + rem_len_bytes], var_header.data(), var_header.size());
        std::memcpy(&buffer[1 + rem_len_bytes + var_header.size()], payload_buf.data(), payload_len);

        return buffer.subspan(0, total_size);
    }

    static std::span<uint8_t> pack_publish(std::span<uint8_t> buffer,
                                           std::string_view topic,
                                           std::span<const uint8_t> payload,
                                           QoS qos = QoS::AtMostOnce,
                                           bool retain = false,
                                           uint16_t packet_id = 0) noexcept {
        if (topic.empty() || (qos != QoS::AtMostOnce && packet_id == 0)) {
            return {};
        }

        const size_t var_header_len = 2 + topic.size() + (qos != QoS::AtMostOnce ? 2 : 0);
        const size_t rem_len = var_header_len + payload.size();

        std::array<uint8_t, 4> rem_len_buf{};
        const size_t rem_len_bytes = encode_remaining_length(rem_len_buf, rem_len);

        const size_t total_size = 1 + rem_len_bytes + rem_len;
        if (total_size > buffer.size()) {
            return {};
        }

        buffer[0] = static_cast<uint8_t>(PacketType::Publish) |
                    ((static_cast<uint8_t>(qos) & 0x03) << 1) |
                    (retain ? 0x01 : 0x00);

        std::memcpy(&buffer[1], rem_len_buf.data(), rem_len_bytes);
        size_t offset = 1 + rem_len_bytes;

        buffer[offset++] = static_cast<uint8_t>((topic.size() >> 8) & 0xFF);
        buffer[offset++] = static_cast<uint8_t>(topic.size() & 0xFF);
        std::memcpy(&buffer[offset], topic.data(), topic.size());
        offset += topic.size();

        if (qos != QoS::AtMostOnce) {
            buffer[offset++] = static_cast<uint8_t>((packet_id >> 8) & 0xFF);
            buffer[offset++] = static_cast<uint8_t>(packet_id & 0xFF);
        }

        if (!payload.empty()) {
            std::memcpy(&buffer[offset], payload.data(), payload.size());
            offset += payload.size();
        }

        return buffer.subspan(0, offset);
    }

private:
    static size_t encode_remaining_length(std::span<uint8_t, 4> buf, size_t length) noexcept {
        size_t bytes = 0;
        do {
            uint8_t byte = static_cast<uint8_t>(length & 0x7F);
            length >>= 7;
            if (length > 0) {
                byte |= 0x80;
            }
            buf[bytes++] = byte;
        } while (length > 0);
        return bytes;
    }

    static size_t write_string(std::span<uint8_t> buf, std::string_view str) noexcept {
        if (buf.size() < str.size() + 2) return 0;
        buf[0] = static_cast<uint8_t>((str.size() >> 8) & 0xFF);
        buf[1] = static_cast<uint8_t>(str.size() & 0xFF);
        std::memcpy(&buf[2], str.data(), str.size());
        return str.size() + 2;
    }
};

} // namespace embedded::mqtt
