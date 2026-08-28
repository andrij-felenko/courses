WelfordAccumulator& operator+=(WelfordAccumulator& dst, const WelfordAccumulator& src) noexcept {
    if (src.count() == 0) return dst;
    if (dst.count() == 0) {
        dst = src;
        return dst;
    }

    const auto n_a = static_cast<double>(dst.count());
    const auto n_b = static_cast<double>(src.count());
    const double n_ab = n_a + n_b;
    const double delta = src.mean() - dst.mean();

    // Об'єднання внутрішнього стану
    return dst;
}
