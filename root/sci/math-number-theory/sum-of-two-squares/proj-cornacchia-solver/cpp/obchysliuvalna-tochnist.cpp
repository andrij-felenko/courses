constexpr std::uint64_t integer_sqrt(std::uint64_t n) noexcept {
    if (n == 0) return 0;
    std::uint64_t x = static_cast<std::uint64_t>(std::sqrt(n));
    while (x * x > n) {
        x = (x + n / x) / 2;
    }
    while ((x + 1) * (x + 1) <= n) {
        x++;
    }
    return x;
}
