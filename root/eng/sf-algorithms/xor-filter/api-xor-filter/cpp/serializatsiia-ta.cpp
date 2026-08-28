namespace algorithms {

template <typename FingerprintType>
class XorFilter {
public:
    /* Серіалізація у вектор байтів */
    [[nodiscard]] std::vector<uint8_t> serialize() const;

    /* Десеріалізація з довільного бінарного зрізу */
    [[nodiscard]] static std::expected<XorFilter, FilterError>
    deserialize(std::span<const uint8_t> buffer);
};

} // namespace algorithms
