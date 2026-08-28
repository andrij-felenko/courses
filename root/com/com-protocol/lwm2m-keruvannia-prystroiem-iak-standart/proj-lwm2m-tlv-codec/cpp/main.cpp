#include <cstdint>
#include <cstddef>
#include <cstring>
#include <span>
#include <optional>
#include <array>
#include <string_view>

namespace lwm2m {

enum class TlvType : uint8_t {
    ObjectInstance   = 0x00,
    ResourceInstance = 0x01,
    MultipleResource = 0x02,
    Resource         = 0x03
};

struct TlvRecord {
    TlvType type{TlvType::Resource};
    uint16_t id{0};
    std::span<const uint8_t> value{};

    [[nodiscard]] std::optional<int64_t> as_int64() const noexcept {
        if (value.empty() || value.size() > 8) return std::nullopt;
        int64_t res = (value[0] & 0x80) ? -1 : 0;
        for (uint8_t b : value) {
            res = (res << 8) | b;
        }
        return res;
    }

    [[nodiscard]] std::optional<float> as_float() const noexcept {
        if (value.size() != 4) return std::nullopt;
        uint32_t raw = (static_cast<uint32_t>(value[0]) << 24) |
                       (static_cast<uint32_t>(value[1]) << 16) |
                       (static_cast<uint32_t>(value[2]) << 8)  |
                       static_cast<uint32_t>(value[3]);
        float f;
        std::memcpy(&f, &raw, sizeof(f));
        return f;
    }

    [[nodiscard]] std::optional<std::string_view> as_string() const noexcept {
        if (value.empty()) return std::string_view{};
        return std::string_view{reinterpret_cast<const char*>(value.data()), value.size()};
    }
};

class TlvDecoder {
public:
    explicit constexpr TlvDecoder(std::span<const uint8_t> buffer) noexcept : buffer_(buffer) {}

    [[nodiscard]] bool has_next() const noexcept {
        return cursor_ < buffer_.size();
    }

    [[nodiscard]] std::optional<TlvRecord> next() noexcept {
        if (cursor_ + 2 > buffer_.size()) {
            return std::nullopt;
        }

        const uint8_t type_byte = buffer_[cursor_++];
        const auto type = static_cast<TlvType>((type_byte >> 6) & 0x03);
        const bool id_is_16bit = (type_byte & (1 << 5)) != 0;
        const uint8_t len_type = (type_byte >> 3) & 0x03;
        const uint8_t val_len_bits = type_byte & 0x07;

        uint16_t id = 0;
        if (!id_is_16bit) {
            id = buffer_[cursor_++];
        } else {
            if (cursor_ + 2 > buffer_.size()) return std::nullopt;
            id = (static_cast<uint16_t>(buffer_[cursor_]) << 8) | buffer_[cursor_ + 1];
            cursor_ += 2;
        }

        uint32_t length = 0;
        if (len_type == 0x00) {
            length = val_len_bits;
        } else if (len_type == 0x01) {
            if (cursor_ + 1 > buffer_.size()) return std::nullopt;
            length = buffer_[cursor_++];
        } else if (len_type == 0x02) {
            if (cursor_ + 2 > buffer_.size()) return std::nullopt;
            length = (static_cast<uint32_t>(buffer_[cursor_]) << 8) | buffer_[cursor_ + 1];
            cursor_ += 2;
        } else if (len_type == 0x03) {
            if (cursor_ + 3 > buffer_.size()) return std::nullopt;
            length = (static_cast<uint32_t>(buffer_[cursor_]) << 16) |
                     (static_cast<uint32_t>(buffer_[cursor_ + 1]) << 8) |
                     buffer_[cursor_ + 2];
            cursor_ += 3;
        }

        if (cursor_ + length > buffer_.size()) {
            return std::nullopt;
        }

        TlvRecord record{
            .type = type,
            .id = id,
            .value = buffer_.subspan(cursor_, length)
        };
        cursor_ += length;

        return record;
    }

private:
    std::span<const uint8_t> buffer_;
    size_t cursor_{0};
};

class TlvEncoder {
public:
    explicit constexpr TlvEncoder(std::span<uint8_t> out_buffer) noexcept : out_(out_buffer) {}

    [[nodiscard]] bool write_int32(uint16_t res_id, int32_t value) noexcept {
        std::array<uint8_t, 4> val_bytes{};
        size_t val_len = 0;

        if (value >= -128 && value <= 127) {
            val_bytes[0] = static_cast<uint8_t>(value & 0xFF);
            val_len = 1;
        } else if (value >= -32768 && value <= 32767) {
            val_bytes[0] = static_cast<uint8_t>((value >> 8) & 0xFF);
            val_bytes[1] = static_cast<uint8_t>(value & 0xFF);
            val_len = 2;
        } else {
            val_bytes[0] = static_cast<uint8_t>((value >> 24) & 0xFF);
            val_bytes[1] = static_cast<uint8_t>((value >> 16) & 0xFF);
            val_bytes[2] = static_cast<uint8_t>((value >> 8) & 0xFF);
            val_bytes[3] = static_cast<uint8_t>(value & 0xFF);
            val_len = 4;
        }

        const size_t header_len = 1 + (res_id > 255 ? 2 : 1);
        if (offset_ + header_len + val_len > out_.size()) {
            return false;
        }

        uint8_t type_byte = (static_cast<uint8_t>(TlvType::Resource) << 6);
        if (res_id > 255) {
            type_byte |= (1 << 5);
        }
        type_byte |= static_cast<uint8_t>(val_len & 0x07);

        out_[offset_++] = type_byte;
        if (res_id > 255) {
            out_[offset_++] = static_cast<uint8_t>((res_id >> 8) & 0xFF);
            out_[offset_++] = static_cast<uint8_t>(res_id & 0xFF);
        } else {
            out_[offset_++] = static_cast<uint8_t>(res_id & 0xFF);
        }

        std::memcpy(&out_[offset_], val_bytes.data(), val_len);
        offset_ += val_len;
        return true;
    }

    [[nodiscard]] size_t bytes_written() const noexcept { return offset_; }

private:
    std::span<uint8_t> out_;
    size_t offset_{0};
};

} // namespace lwm2m
