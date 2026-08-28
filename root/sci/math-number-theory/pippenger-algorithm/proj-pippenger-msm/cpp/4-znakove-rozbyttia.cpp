namespace msm {

struct SignedDigit {
    int32_t value{0};
    bool is_negative{false};
};

/* Вилучення знакової цифри з переносом */
[[nodiscard]] SignedDigit extract_signed_window(
    const FieldElement& scalar,
    uint32_t window_idx,
    uint32_t c,
    int32_t& carry
) noexcept {
    const uint32_t raw = extract_window(scalar, window_idx, c) + static_cast<uint32_t>(carry);
    carry = 0;

    const int32_t half = 1 << (c - 1);
    const int32_t max_val = 1 << c;
    SignedDigit res;

    if (static_cast<int32_t>(raw) >= half) {
        res.value = max_val - static_cast<int32_t>(raw);
        res.is_negative = true;
        carry = 1;
    } else {
        res.value = static_cast<int32_t>(raw);
        res.is_negative = false;
    }
    return res;
}

} // namespace msm
