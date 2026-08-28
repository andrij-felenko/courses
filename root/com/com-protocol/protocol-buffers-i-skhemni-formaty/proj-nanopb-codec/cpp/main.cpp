#include <cstdint>
#include <cstddef>
#include <cstring>
#include <span>
#include <array>
#include <optional>
#include <expected>
#include <string_view>

namespace proto {

struct GpsCoords {
    int32_t lat_e7{0};
    int32_t lon_e7{0};
};

struct TelemetryPacket {
    uint32_t timestamp_s{0};
    uint32_t sensor_id{0};
    int32_t  temperature_c100{0};
    uint32_t battery_mv{0};
    std::optional<GpsCoords> location{std::nullopt};
};

enum class CodecError {
    BufferOverflow,
    UnexpectedEof,
    VarintOverflow,
    InvalidWireType,
    MalformedSubmessage
};

class BitCodec {
public:
    static constexpr uint32_t zigzag_encode(int32_t n) noexcept {
        return static_cast<uint32_t>((n << 1) ^ (n >> 31));
    }

    static constexpr int32_t zigzag_decode(uint32_t z) noexcept {
        return static_cast<int32_t>((z >> 1) ^ -static_cast<int32_t>(z & 1));
    }
};

class OutputStream {
public:
    explicit constexpr OutputStream(std::span<uint8_t> buffer) noexcept
        : buffer_(buffer), written_(0) {}

    [[nodiscard]] size_t bytes_written() const noexcept { return written_; }

    [[nodiscard]] bool write_varint(uint64_t val) noexcept {
        while (val >= 0x80) {
            if (written_ >= buffer_.size()) return false;
            buffer_[written_++] = static_cast<uint8_t>((val & 0x7F) | 0x80);
            val >>= 7;
        }
        if (written_ >= buffer_.size()) return false;
        buffer_[written_++] = static_cast<uint8_t>(val & 0x7F);
        return true;
    }

    [[nodiscard]] bool write_tag(uint32_t field_num, uint8_t wire_type) noexcept {
        return write_varint((static_cast<uint64_t>(field_num) << 3) | (wire_type & 0x07));
    }

    [[nodiscard]] bool write_bytes(std::span<const uint8_t> data) noexcept {
        if (written_ + data.size() > buffer_.size()) return false;
        std::memcpy(&buffer_[written_], data.data(), data.size());
        written_ += data.size();
        return true;
    }

private:
    std::span<uint8_t> buffer_;
    size_t written_;
};

class InputStream {
public:
    explicit constexpr InputStream(std::span<const uint8_t> buffer) noexcept
        : buffer_(buffer), cursor_(0) {}

    [[nodiscard]] size_t bytes_left() const noexcept { return buffer_.size() - cursor_; }

    [[nodiscard]] std::expected<uint64_t, CodecError> read_varint() noexcept {
        uint64_t result = 0;
        int bitpos = 0;
        while (bitpos < 64) {
            if (cursor_ >= buffer_.size()) {
                return std::unexpected(CodecError::UnexpectedEof);
            }
            const uint8_t b = buffer_[cursor_++];
            result |= static_cast<uint64_t>(b & 0x7F) << bitpos;
            if ((b & 0x80) == 0) {
                return result;
            }
            bitpos += 7;
        }
        return std::unexpected(CodecError::VarintOverflow);
    }

    [[nodiscard]] bool skip_bytes(size_t count) noexcept {
        if (cursor_ + count > buffer_.size()) return false;
        cursor_ += count;
        return true;
    }

    [[nodiscard]] std::expected<std::span<const uint8_t>, CodecError> read_subspan(size_t count) noexcept {
        if (cursor_ + count > buffer_.size()) {
            return std::unexpected(CodecError::UnexpectedEof);
        }
        std::span<const uint8_t> sub = buffer_.subspan(cursor_, count);
        cursor_ += count;
        return sub;
    }

private:
    std::span<const uint8_t> buffer_;
    size_t cursor_;
};

// Серіалізатор
[[nodiscard]] inline std::expected<size_t, CodecError> serialize(
    const TelemetryPacket& msg,
    std::span<uint8_t> output_buffer) noexcept
{
    OutputStream stream(output_buffer);

    if (msg.timestamp_s != 0) {
        if (!stream.write_tag(1, 0) || !stream.write_varint(msg.timestamp_s))
            return std::unexpected(CodecError::BufferOverflow);
    }
    if (msg.sensor_id != 0) {
        if (!stream.write_tag(2, 0) || !stream.write_varint(msg.sensor_id))
            return std::unexpected(CodecError::BufferOverflow);
    }
    if (msg.temperature_c100 != 0) {
        const auto zz = BitCodec::zigzag_encode(msg.temperature_c100);
        if (!stream.write_tag(3, 0) || !stream.write_varint(zz))
            return std::unexpected(CodecError::BufferOverflow);
    }
    if (msg.battery_mv != 0) {
        if (!stream.write_tag(4, 0) || !stream.write_varint(msg.battery_mv))
            return std::unexpected(CodecError::BufferOverflow);
    }
    if (msg.location.has_value()) {
        std::array<uint8_t, 32> sub_buf{};
        OutputStream sub_stream(sub_buf);
        if (msg.location->lat_e7 != 0) {
            sub_stream.write_tag(1, 0);
            sub_stream.write_varint(BitCodec::zigzag_encode(msg.location->lat_e7));
        }
        if (msg.location->lon_e7 != 0) {
            sub_stream.write_tag(2, 0);
            sub_stream.write_varint(BitCodec::zigzag_encode(msg.location->lon_e7));
        }

        if (!stream.write_tag(5, 2) ||
            !stream.write_varint(sub_stream.bytes_written()) ||
            !stream.write_bytes(std::span{sub_buf.data(), sub_stream.bytes_written()})) {
            return std::unexpected(CodecError::BufferOverflow);
        }
    }

    return stream.bytes_written();
}

// Десеріалізатор
[[nodiscard]] inline std::expected<TelemetryPacket, CodecError> deserialize(
    std::span<const uint8_t> input_buffer) noexcept
{
    TelemetryPacket msg{};
    InputStream stream(input_buffer);

    while (stream.bytes_left() > 0) {
        auto key_res = stream.read_varint();
        if (!key_res) return std::unexpected(key_res.error());

        const uint32_t tag = static_cast<uint32_t>(*key_res >> 3);
        const uint8_t wire_type = static_cast<uint8_t>(*key_res & 0x07);

        if (wire_type == 0) { // Varint
            auto val_res = stream.read_varint();
            if (!val_res) return std::unexpected(val_res.error());
            const uint64_t val = *val_res;

            switch (tag) {
                case 1: msg->timestamp_s = static_cast<uint32_t>(val); break;
                case 2: msg->sensor_id = static_cast<uint32_t>(val); break;
                case 3: msg->temperature_c100 = BitCodec::zigzag_decode(static_cast<uint32_t>(val)); break;
                case 4: msg->battery_mv = static_cast<uint32_t>(val); break;
                default: break; // Пропуск незнайомого поля
            }
        } else if (wire_type == 2) { // Length-delimited
            auto len_res = stream.read_varint();
            if (!len_res) return std::unexpected(len_res.error());

            auto sub_bytes = stream.read_subspan(static_cast<size_t>(*len_res));
            if (!sub_bytes) return std::unexpected(sub_bytes.error());

            if (tag == 5) {
                GpsCoords coords{};
                InputStream sub_stream(*sub_bytes);
                while (sub_stream.bytes_left() > 0) {
                    auto sub_key = sub_stream.read_varint();
                    auto sub_val = sub_stream.read_varint();
                    if (!sub_key || !sub_val) return std::unexpected(CodecError::MalformedSubmessage);
                    const uint32_t sub_tag = static_cast<uint32_t>(*sub_key >> 3);
                    if (sub_tag == 1) coords.lat_e7 = BitCodec::zigzag_decode(static_cast<uint32_t>(*sub_val));
                    else if (sub_tag == 2) coords.lon_e7 = BitCodec::zigzag_decode(static_cast<uint32_t>(*sub_val));
                }
                msg.location = coords;
            }
        } else {
            return std::unexpected(CodecError::InvalidWireType);
        }
    }
    return msg;
}

} // namespace proto
