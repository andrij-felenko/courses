namespace jaccard {

class JaccardEngine {
public:
    explicit JaccardEngine(Config config);
    ~JaccardEngine();

    JaccardEngine(const JaccardEngine&) = delete;
    JaccardEngine& operator=(const JaccardEngine&) = delete;

    JaccardEngine(JaccardEngine&&) noexcept;
    JaccardEngine& operator=(JaccardEngine&&) noexcept;

    [[nodiscard]] static double compute_exact(
        std::span<const uint64_t> a,
        std::span<const uint64_t> b
    );

    [[nodiscard]] static bool check_size_filter(
        size_t len_a,
        size_t len_b,
        double threshold
    ) noexcept;

    [[nodiscard]] std::vector<uint64_t> compute_signature(
        std::span<const uint64_t> shingles
    ) const;

    [[nodiscard]] static double compare_signatures(
        std::span<const uint64_t> sig_a,
        std::span<const uint64_t> sig_b
    );

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace jaccard
