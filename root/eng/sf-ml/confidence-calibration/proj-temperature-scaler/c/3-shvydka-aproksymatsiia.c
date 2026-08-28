static inline float fast_expf_approx(float x) {
    /* Діапазон валідності x in [-8.0, 0.0] */
    if (x < -8.0f) return 0.0f;
    union {
        float f;
        int32_t i;
    } eco;
    eco.i = (int32_t)(12102203.0f * x + 1064866805.0f);
    return eco.f;
}
