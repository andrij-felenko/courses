#include <cstdint>
#include <cstddef>
#include <span>
#include <optional>
#include <string_view>

struct FontUnicodeRange {
    uint32_t unicode_first;
    uint32_t unicode_last;
    uint32_t glyph_index_offset;
};

struct FontGlyphDesc {
    uint8_t  box_w;
    uint8_t  box_h;
    int8_t   off_x;
    int8_t   off_y;
    uint8_t  adv_w;
    uint8_t  reserved;
    uint32_t bitmap_offset;
};

class EmbeddedFont {
public:
    struct Header {
        uint32_t magic;
        uint8_t  version;
        uint8_t  bpp;
        int8_t   ascent;
        int8_t   descent;
        uint16_t range_count;
        uint32_t glyph_count;
    };

    constexpr EmbeddedFont(const Header &header,
                           std::span<const FontUnicodeRange> ranges,
                           std::span<const FontGlyphDesc> glyphs,
                           std::span<const uint8_t> bitmap_data) noexcept
        : header_(header), ranges_(ranges), glyphs_(glyphs), bitmap_data_(bitmap_data) {}

    [[nodiscard]] std::optional<FontGlyphDesc> find_glyph(uint32_t codepoint) const noexcept {
        for (const auto &range : ranges_) {
            if (codepoint >= range.unicode_first && codepoint <= range.unicode_last) {
                size_t idx = range.glyph_index_offset + (codepoint - range.unicode_first);
                if (idx < glyphs_.size()) {
                    return glyphs_[idx];
                }
                break;
            }
        }
        return std::nullopt;
    }

    [[nodiscard]] std::span<const uint8_t> get_bitmap_slice(const FontGlyphDesc &desc) const noexcept {
        size_t bytes_per_row = (desc.box_w * header_.bpp + 7) / 8;
        size_t total_bytes = bytes_per_row * desc.box_h;
        if (desc.bitmap_offset + total_bytes <= bitmap_data_.size()) {
            return bitmap_data_.subspan(desc.bitmap_offset, total_bytes);
        }
        return {};
    }

    [[nodiscard]] int8_t ascent() const noexcept { return header_.ascent; }
    [[nodiscard]] int8_t descent() const noexcept { return header_.descent; }
    [[nodiscard]] uint8_t bpp() const noexcept { return header_.bpp; }

private:
    Header header_;
    std::span<const FontUnicodeRange> ranges_;
    std::span<const FontGlyphDesc> glyphs_;
    std::span<const uint8_t> bitmap_data_;
};
