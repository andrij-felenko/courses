// Ідіоматичне калібрування Softmax у C++20 з верифікацією меж таблиці
[[nodiscard]] constexpr uint16_t fast_calibrated_confidence_q15(
    int16_t logit_max,
    int16_t logit_sum,
    int16_t temp_q8,
    std::span<const uint16_t> exp_lut
) noexcept {
    const int32_t raw_scaled = ((int32_t)(logit_max - logit_sum) << 8) / temp_q8;
    const size_t index = static_cast<size_t>(std::clamp(raw_scaled, 0, 2048));
    return (index < exp_lut.size()) ? exp_lut[index] : 0;
}
