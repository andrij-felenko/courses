#include <cstdint>
#include <cstddef>
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <expected>
#include <array>

namespace ndef {

enum class ParseError {
    BufferTooSmall,
    InvalidHeader,
    UnsupportedTnf
};

enum class Tnf : uint8_t {
    Empty = 0x00,
    WellKnown = 0x01,
    MimeMedia = 0x02,
    AbsoluteUri = 0x03,
    External = 0x04,
    Unknown = 0x05,
    Unchanged = 0x06
};

struct RecordView {
    Tnf tnf{Tnf::Empty};
    bool is_first{false};
    bool is_last{false};
    std::string_view type{};
    std::string_view id{};
    std::span<const uint8_t> payload{};
};

constexpr std::array<std::string_view, 11> URI_PREFIXES = {
    "",
    "http://www.",
    "https://www.",
    "http://",
    "https://",
    "tel:",
    "mailto:",
    "ftp://anonymous:anonymous@",
    "ftp://ftp.",
    "ftps://",
    "sftp://"
};

class Parser {
public:
    static std::expected<std::pair<RecordView, size_t>, ParseError> parse(std::span<const uint8_t> buffer) {
        if (buffer.size() < 2) return std::unexpected(ParseError::BufferTooSmall);

        uint8_t header = buffer[0];
        RecordView rec;
        rec.is_first = (header & 0x80) != 0;
        rec.is_last = (header & 0x40) != 0;
        rec.tnf = static_cast<Tnf>(header & 0x07);

        bool is_short = (header & 0x10) != 0;
        bool has_id = (header & 0x08) != 0;

        size_t offset = 1;
        uint8_t type_len = buffer[offset++];

        uint32_t payload_len = 0;
        if (is_short) {
            if (offset >= buffer.size()) return std::unexpected(ParseError::BufferTooSmall);
            payload_len = buffer[offset++];
        } else {
            if (offset + 4 > buffer.size()) return std::unexpected(ParseError::BufferTooSmall);
            payload_len = (static_cast<uint32_t>(buffer[offset]) << 24) |
                          (static_cast<uint32_t>(buffer[offset + 1]) << 16) |
                          (static_cast<uint32_t>(buffer[offset + 2]) << 8) |
                          static_cast<uint32_t>(buffer[offset + 3]);
            offset += 4;
        }

        uint8_t id_len = 0;
        if (has_id) {
            if (offset >= buffer.size()) return std::unexpected(ParseError::BufferTooSmall);
            id_len = buffer[offset++];
        }

        if (offset + type_len + id_len + payload_len > buffer.size()) {
            return std::unexpected(ParseError::BufferTooSmall);
        }

        rec.type = std::string_view(reinterpret_cast<const char*>(buffer.data() + offset), type_len);
        offset += type_len;

        if (has_id) {
            rec.id = std::string_view(reinterpret_cast<const char*>(buffer.data() + offset), id_len);
            offset += id_len;
        }

        rec.payload = buffer.subspan(offset, payload_len);
        offset += payload_len;

        return std::make_pair(rec, offset);
    }

    static std::expected<std::string, ParseError> decode_uri(const RecordView& rec) {
        if (rec.tnf != Tnf::WellKnown || rec.type != "U" || rec.payload.empty()) {
            return std::unexpected(ParseError::InvalidHeader);
        }

        uint8_t prefix_idx = rec.payload[0];
        std::string_view prefix = "";
        if (prefix_idx < URI_PREFIXES.size()) {
            prefix = URI_PREFIXES[prefix_idx];
        }

        std::string result(prefix);
        result.append(reinterpret_cast<const char*>(rec.payload.data() + 1), rec.payload.size() - 1);
        return result;
    }
};

} // namespace ndef
