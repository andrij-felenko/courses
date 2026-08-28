constexpr std::optional<int> parse_wday_token(std::string_view sv) noexcept {
    if (sv.size() < 2) return std::nullopt;
    uint16_t tag = (static_cast<uint16_t>(sv[0]) << 8) | static_cast<uint16_t>(sv[1]);
    switch (tag) {
        case 0x5355: return 0; // "SU"
        case 0x4D4F: return 1; // "MO"
        case 0x5455: return 2; // "TU"
        case 0x5745: return 3; // "WE"
        case 0x5448: return 4; // "TH"
        case 0x4652: return 5; // "FR"
        case 0x5341: return 6; // "SA"
        default:     return std::nullopt;
    }
}
