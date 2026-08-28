// Розрахунок геометричної ширини рядка на C++20
[[nodiscard]] uint16_t get_string_width(const embedded_font_t &font, std::string_view utf8_str) noexcept {
    uint16_t total_width = 0;
    std::span<const uint8_t> bytes{
        reinterpret_cast<const uint8_t*>(utf8_str.data()),
        utf8_str.size()
    };
    
    while (!bytes.empty()) {
        auto res = utf8_decode_next(bytes);
        bytes = bytes.subspan(res.bytes_consumed);
        if (res.code_point == 0xFFFD) continue;
        
        if (const auto *glyph = font_find_glyph(&font, static_cast<uint32_t>(res.code_point))) {
            total_width += glyph->adv_w;
        }
    }
    return total_width;
}
