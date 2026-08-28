namespace msm {

/* Вилучення c-бітного вікна скаляра */
[[nodiscard]] constexpr uint32_t extract_window(const FieldElement& scalar, uint32_t window_idx, uint32_t c) noexcept {
    const uint32_t bit_offset = window_idx * c;
    const uint32_t word_idx = bit_offset / 64;
    const uint32_t shift = bit_offset % 64;
    const uint32_t mask = (1U << c) - 1U;

    if (word_idx >= FIELD_WORDS) {
        return 0;
    }

    uint64_t val = scalar.d[word_idx] >> shift;
    if (shift + c > 64 && word_idx + 1 < FIELD_WORDS) {
        val |= scalar.d[word_idx + 1] << (64 - shift);
    }
    return static_cast<uint32_t>(val & mask);
}

} // namespace msm
