#include <iostream>
#include <span>
#include <string_view>
#include <vector>
#include <cstdint>
#include <expected>
#include <bit>

namespace cmaf {

enum class ParseError {
    UnexpectedEof,
    InvalidBoxSize,
    InvalidVersion,
    MalformedStructure
};

struct FourCC {
    uint32_t value{0};

    [[nodiscard]] constexpr std::string_view as_string() const noexcept {
        return std::string_view(reinterpret_cast<const char*>(&value), 4);
    }
};

struct BoxHeader {
    FourCC type;
    uint64_t total_size{0};
    uint32_t header_size{8};
};

struct ChunkSummary {
    uint32_t sequence_number{0};
    uint32_t track_id{0};
    uint64_t base_decode_time{0};
    uint32_t sample_count{0};
    uint64_t duration_ticks{0};
    bool is_sync_point{false};
    bool base_is_moof{false};
};

class BoxParser {
public:
    static uint32_t read_be32(std::span<const uint8_t> bytes) noexcept {
        return (static_cast<uint32_t>(bytes[0]) << 24) |
               (static_cast<uint32_t>(bytes[1]) << 16) |
               (static_cast<uint32_t>(bytes[2]) << 8)  |
               (static_cast<uint32_t>(bytes[3]));
    }

    static uint64_t read_be64(std::span<const uint8_t> bytes) noexcept {
        return (static_cast<uint64_t>(read_be32(bytes.subspan(0, 4))) << 32) |
               (static_cast<uint64_t>(read_be32(bytes.subspan(4, 4))));
    }

    static std::expected<BoxHeader, ParseError> parse_header(std::span<const uint8_t> data) noexcept {
        if (data.size() < 8) return std::unexpected(ParseError::UnexpectedEof);

        uint32_t s32 = read_be32(data.subspan(0, 4));
        FourCC type{read_be32(data.subspan(4, 4))};
        uint64_t total = s32;
        uint32_t hsz = 8;

        if (s32 == 1) {
            if (data.size() < 16) return std::unexpected(ParseError::UnexpectedEof);
            total = read_be64(data.subspan(8, 8));
            hsz = 16;
        } else if (s32 == 0) {
            total = data.size();
        }

        if (total < hsz || total > data.size()) {
            return std::unexpected(ParseError::InvalidBoxSize);
        }

        return BoxHeader{type, total, hsz};
    }

    static std::expected<ChunkSummary, ParseError> inspect_chunk(std::span<const uint8_t> chunk) {
        ChunkSummary summary;
        size_t offset = 0;

        while (offset + 8 <= chunk.size()) {
            auto h_res = parse_header(chunk.subspan(offset));
            if (!h_res) return std::unexpected(h_res.error());

            const auto& hdr = *h_res;
            auto body = chunk.subspan(offset + hdr.header_size, hdr.total_size - hdr.header_size);

            if (hdr.type.value == 0x6D6F6F66) { // 'moof'
                size_t in_off = 0;
                while (in_off + 8 <= body.size()) {
                    auto in_h = parse_header(body.subspan(in_off));
                    if (!in_h) break;
                    auto in_body = body.subspan(in_off + in_h->header_size, in_h->total_size - in_h->header_size);

                    if (in_h->type.value == 0x6D666864 && in_body.size() >= 8) { // 'mfhd'
                        summary.sequence_number = read_be32(in_body.subspan(4, 4));
                    } else if (in_h->type.value == 0x74726166) { // 'traf'
                        parse_traf(in_body, summary);
                    }
                    in_off += in_h->total_size;
                }
            }
            offset += hdr.total_size;
        }
        return summary;
    }

private:
    static void parse_traf(std::span<const uint8_t> traf_body, ChunkSummary& summary) {
        size_t off = 0;
        while (off + 8 <= traf_body.size()) {
            auto h = parse_header(traf_body.subspan(off));
            if (!h) break;
            auto body = traf_body.subspan(off + h->header_size, h->total_size - h->header_size);

            if (h->type.value == 0x74666474 && !body.empty()) { // 'tfdt'
                uint8_t ver = body[0];
                if (ver == 1 && body.size() >= 12) {
                    summary.base_decode_time = read_be64(body.subspan(4, 8));
                } else if (ver == 0 && body.size() >= 8) {
                    summary.base_decode_time = read_be32(body.subspan(4, 4));
                }
            } else if (h->type.value == 0x74666864 && body.size() >= 8) { // 'tfhd'
                uint32_t flags = read_be32(body.subspan(0, 4)) & 0x00FFFFFF;
                summary.track_id = read_be32(body.subspan(4, 4));
                summary.base_is_moof = (flags & 0x020000) != 0;
            } else if (h->type.value == 0x7472756E && body.size() >= 8) { // 'trun'
                uint32_t flags = read_be32(body.subspan(0, 4)) & 0x00FFFFFF;
                summary.sample_count = read_be32(body.subspan(4, 4));

                size_t p = 8;
                if (flags & 0x000001) p += 4; // data_offset
                if (flags & 0x000004) {       // first_sample_flags
                    if (p + 4 <= body.size()) {
                        uint32_t fs = read_be32(body.subspan(p, 4));
                        if ((fs & 0x00010000) == 0) summary.is_sync_point = true;
                        p += 4;
                    }
                }
                bool has_dur = (flags & 0x000100) != 0;
                bool has_flags = (flags & 0x000400) != 0;

                for (uint32_t i = 0; i < summary.sample_count; ++i) {
                    if (has_dur && p + 4 <= body.size()) {
                        summary.duration_ticks += read_be32(body.subspan(p, 4));
                        p += 4;
                    }
                    if (flags & 0x000200) p += 4; // sample_size
                    if (has_flags && p + 4 <= body.size()) {
                        uint32_t sf = read_be32(body.subspan(p, 4));
                        if ((sf & 0x00010000) == 0) summary.is_sync_point = true;
                        p += 4;
                    }
                    if (flags & 0x000800) p += 4; // sample_cto
                }
            }
            off += h->total_size;
        }
    }
};

} // namespace cmaf
