// Алгоритм розриву рядка за словами на C++20
size_t text_wrap(const embedded_font_t &font, std::string_view text, uint16_t max_width,
                 std::span<uint16_t> line_offsets) noexcept {
    if (text.empty() || line_offsets.empty()) return 0;
    
    size_t line_count = 0;
    line_offsets[line_count++] = 0;
    
    std::span<const uint8_t> bytes{
        reinterpret_cast<const uint8_t*>(text.data()),
        text.size()
    };
    
    size_t cur_offset = 0;
    size_t line_start = 0;
    std::optional<size_t> last_space_offset;
    uint16_t current_line_width = 0;
    
    while (!bytes.empty()) {
        size_t char_start = cur_offset;
        auto res = utf8_decode_next(bytes);
        bytes = bytes.subspan(res.bytes_consumed);
        cur_offset += res.bytes_consumed;
        if (res.code_point == 0xFFFD) continue;
        
        if (res.code_point == U' ') {
            last_space_offset = char_start;
        }
        
        const auto *glyph = font_find_glyph(&font, static_cast<uint32_t>(res.code_point));
        uint8_t adv = glyph ? glyph->adv_w : 0;
        
        if (current_line_width + adv > max_width) {
            if (line_count >= line_offsets.size()) break;
            
            if (last_space_offset && *last_space_offset > line_start) {
                line_offsets[line_count++] = static_cast<uint16_t>(*last_space_offset + 1);
                line_start = *last_space_offset + 1;
                last_space_offset = std::nullopt;
                current_line_width = 0;
            } else {
                line_offsets[line_count++] = static_cast<uint16_t>(char_start);
                line_start = char_start;
                current_line_width = adv;
            }
        } else {
            current_line_width += adv;
        }
    }
    return line_count;
}
