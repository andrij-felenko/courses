namespace pairing {

/* Спеціалізований функтор хешування пар координат */
struct PairHash {
    [[nodiscard]] size_t operator()(const Pair32& p) const noexcept {
        auto code_opt = cantor_encode(p.x, p.y);
        if (!code_opt) return 0;

        /* Фіналізатор MurmurHash3 fmix64 для усунення діагональної кластеризації */
        uint64_t k = *code_opt;
        k ^= k >> 33;
        k *= 0xff51afd7ed558ccdULL;
        k ^= k >> 33;
        k *= 0xc4ceb9fe1a85ec53ULL;
        k ^= k >> 33;
        return static_cast<size_t>(k);
    }
};

} // namespace pairing
