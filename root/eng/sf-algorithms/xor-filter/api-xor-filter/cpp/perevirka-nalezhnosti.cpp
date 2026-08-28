namespace algorithms {

template <typename FingerprintType>
class XorFilter {
public:
    /* Швидка перевірка належності ключа O(1) */
    [[nodiscard]] bool contains(uint64_t key) const noexcept;
};

} // namespace algorithms
