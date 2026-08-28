#include <cstdint>
#include <cstddef>
#include <cstring>
#include <span>
#include <expected>

namespace telemetry {

struct Reading {
    uint32_t timestamp_s{0};
    uint32_t sensor_id{0};
    int32_t  temperature_c100{0};
    uint32_t battery_mv{0};
};

enum class DecodeError {
    UnexpectedEof,
    InvalidVarint,
    UnsupportedWireType
};

class WireCodec {
public:
    static constexpr uint32_t zigzag_encode(int32_t n) noexcept {
        return static_cast<uint32_t>((n << 1) ^ (n >> 31));
    }

    static constexpr int32_t zigzag_decode(uint32_t z) noexcept {
        return static_cast<int32_t>((z >> 1) ^ -static_cast<int32_t>(z & 1));
    }

    static size_t encode_varint(std::span<uint8_t> dest, uint64_t val) noexcept {
        size_t written = 0;
        while (val >= 0x80) {
            if (written >= dest.size()) return 0;
            dest[written++] = static_cast<uint8_t>((val & 0x7F) | 0x80);
            val >>= 7;
        }
        if (written >= dest.size()) return 0;
        dest[written++] = static_cast<uint8_t>(val & 0x7F);
        return written;
    }

    static size_t encode_tag(std::span<uint8_t> dest, uint32_t field_num, uint8_t wire_type) noexcept {
        return encode_varint(dest, (static_cast<uint64_t>(field_num) << 3) | (wire_type & 0x07));
    }
};

[[nodiscard]] inline size_t serialize(const Reading& msg, std::span<uint8_t> buffer) noexcept {
    size_t offset = 0;

    auto write_field = [&](uint32_t tag, uint64_t val) noexcept -> bool {
        if (val == 0) return true;
        size_t t_bytes = WireCodec::encode_tag(buffer.subspan(offset), tag, 0);
        if (t_bytes == 0) return false;
        offset += t_bytes;

        size_t v_bytes = WireCodec::encode_varint(buffer.subspan(offset), val);
        if (v_bytes == 0) return false;
        offset += v_bytes;
        return true;
    };

    if (!write_field(1, msg.timestamp_s)) return 0;
    if (!write_field(2, msg.sensor_id)) return 0;
    if (!write_field(3, WireCodec::zigzag_encode(msg.temperature_c100))) return 0;
    if (!write_field(4, msg.battery_mv)) return 0;

    return offset;
}

[[nodiscard]] inline std::expected<Reading, DecodeError> deserialize(std::span<const uint8_t> buffer) noexcept {
    Reading msg{};
    size_t cursor = 0;

    while (cursor < buffer.size()) {
        uint64_t key = 0;
        int bitpos = 0;
        while (bitpos < 64) {
            if (cursor >= buffer.size()) return std::unexpected(DecodeError::UnexpectedEof);
            uint8_t b = buffer[cursor++];
            key |= static_cast<uint64_t>(b & 0x7F) << bitpos;
            if ((b & 0x80) == 0) break;
            bitpos += 7;
        }

        const uint32_t tag = static_cast<uint32_t>(key >> 3);
        const uint8_t wire_type = static_cast<uint8_t>(key & 0x07);

        if (wire_type == 0) {
            uint64_t val = 0;
            bitpos = 0;
            while (bitpos < 64) {
                if (cursor >= buffer.size()) return std::unexpected(DecodeError::UnexpectedEof);
                uint8_t b = buffer[cursor++];
                val |= static_cast<uint64_t>(b & 0x7F) << bitpos;
                if ((b & 0x80) == 0) break;
                bitpos += 7;
            }
            switch (tag) {
                case 1: msg->timestamp_s = static_cast<uint32_t>(val); break;
                case 2: msg->sensor_id = static_cast<uint32_t>(val); break;
                case 3: msg->temperature_c100 = WireCodec::zigzag_decode(static_cast<uint32_t>(val)); break;
                case 4: msg->battery_mv = static_cast<uint32_t>(val); break;
                default: break; // Ігноруємо невідоме поле
            }
        } else if (wire_type == 1) {
            if (cursor + 8 > buffer.size()) return std::unexpected(DecodeError::UnexpectedEof);
            cursor += 8;
        } else if (wire_type == 2) {
            uint64_t len = 0;
            bitpos = 0;
            while (bitpos < 64) {
                if (cursor >= buffer.size()) return std::unexpected(DecodeError::UnexpectedEof);
                uint8_t b = buffer[cursor++];
                len |= static_cast<uint64_t>(b & 0x7F) << bitpos;
                if ((b & 0x80) == 0) break;
                bitpos += 7;
            }
            if (cursor + len > buffer.size()) return std::unexpected(DecodeError::UnexpectedEof);
            cursor += static_cast<size_t>(len);
        } else if (wire_type == 5) {
            if (cursor + 4 > buffer.size()) return std::unexpected(DecodeError::UnexpectedEof);
            cursor += 4;
        } else {
            return std::unexpected(DecodeError::UnsupportedWireType);
        }
    }
    return msg;
}

} // namespace telemetry
