constexpr std::optional<uint32_t> parse_uint_fast(std::string_view& sv) noexcept {
    if (sv.empty() || sv.front() < '0' || sv.front() > '9') return std::nullopt;
    uint32_t v = 0;
    size_t idx = 0;
    while (idx < sv.size() && sv[idx] >= '0' && sv[idx] <= '9') {
        v = v * 10 + static_cast<uint32_t>(sv[idx] - '0');
        idx++;
    }
    sv.remove_prefix(idx);
    return v;
}
