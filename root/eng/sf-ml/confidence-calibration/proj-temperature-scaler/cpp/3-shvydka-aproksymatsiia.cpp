constexpr float fast_expf_approx(float x) noexcept {
    // Діапазон валідності x in [-8.0, 0.0]
    if (x < -8.0f) return 0.0f;
    union {
        float f;
        std::int32_t i;
    } eco;
    eco.i = static_cast<std::int32_t>(12102203.0f * x + 1064866805.0f);
    return eco.f;
}
