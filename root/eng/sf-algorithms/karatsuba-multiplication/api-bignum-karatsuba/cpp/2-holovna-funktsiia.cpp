namespace Bignum {

[[nodiscard]] std::expected<void, Status> multiplyKaratsuba(
    std::span<const Limb> a,
    std::span<const Limb> b,
    std::span<Limb> out,
    std::span<Limb> scratch
) noexcept;

} // namespace Bignum
