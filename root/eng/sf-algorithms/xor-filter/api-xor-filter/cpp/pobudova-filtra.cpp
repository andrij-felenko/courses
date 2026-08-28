namespace algorithms {

template <typename FingerprintType>
class XorFilter {
public:
    /* Фабричний метод побудови з неперервного діапазону ключів */
    [[nodiscard]] static std::expected<XorFilter, FilterError>
    build(std::span<const uint64_t> keys);
};

} // namespace algorithms
