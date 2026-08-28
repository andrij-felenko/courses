namespace core::hash {

struct alignas(16) Hash128 {
    std::uint64_t low{0};
    std::uint64_t high{0};

    [[nodiscard]] constexpr auto operator<=>(const Hash128&) const noexcept = default;
};

[[nodiscard]] Hash128 hash128_fn(std::span<const std::uint8_t> input, std::uint64_t seed = 0) noexcept;

} // namespace core::hash
