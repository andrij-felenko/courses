double compute_exact_sorted(
    std::span<const uint64_t> set_a,
    std::span<const uint64_t> set_b
);

bool pass_size_filter(
    size_t len_a,
    size_t len_b,
    double threshold
) noexcept;
