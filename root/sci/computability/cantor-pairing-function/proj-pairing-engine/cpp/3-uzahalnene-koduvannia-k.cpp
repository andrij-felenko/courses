namespace pairing {

/* Кодування послідовності довільної довжини через std::span у C++20 */
[[nodiscard]] inline std::optional<uint64_t> encode_tuple(std::span<const uint32_t> values) noexcept {
    if (values.empty()) return std::nullopt;
    if (values.size() == 1) return values.front();

    uint64_t current = values[0];
    for (size_t i = 1; i < values.size(); ++i) {
        const uint64_t w = current + values[i];
        if (w > 6074000999ULL) return std::nullopt;
        current = (w * (w + 1)) / 2 + values[i];
    }

    return current;
}

/* Декодування у динамічний вектор координат */
[[nodiscard]] inline std::optional<std::vector<uint32_t>> decode_tuple(uint64_t code, size_t dimension) {
    if (dimension == 0) return std::nullopt;
    std::vector<uint32_t> result(dimension);

    if (dimension == 1) {
        if (code > UINT32_MAX) return std::nullopt;
        result[0] = static_cast<uint32_t>(code);
        return result;
    }

    uint64_t current = code;
    for (size_t i = dimension - 1; i >= 1; --i) {
        if (current >= (UINT64_MAX / 8)) return std::nullopt;
        const uint64_t s = isqrt64(8 * current + 1);
        const uint64_t w = (s - 1) / 2;
        const uint64_t base = (w * (w + 1)) / 2;
        const uint64_t val = current - base;
        current = w - val;

        if (val > UINT32_MAX) return std::nullopt;
        result[i] = static_cast<uint32_t>(val);
    }

    if (current > UINT32_MAX) return std::nullopt;
    result[0] = static_cast<uint32_t>(current);
    return result;
}

} // namespace pairing
