namespace graph_walk {

class GraphWalkEngine {
public:
    explicit GraphWalkEngine(GraphSpec spec);
    ~GraphWalkEngine();

    // Заборона копіювання, дозволено переміщення
    GraphWalkEngine(const GraphWalkEngine&) = delete;
    GraphWalkEngine& operator=(const GraphWalkEngine&) = delete;
    GraphWalkEngine(GraphWalkEngine&&) noexcept;
    GraphWalkEngine& operator=(GraphWalkEngine&&) noexcept;

    // Метод s-t зв'язності
    [[nodiscard]] bool is_connected(size_t s, size_t t, uint32_t trials = 5) const;

    // Обчислення PageRank
    [[nodiscard]] std::vector<double> pagerank(const WalkConfig& config, uint64_t num_walks) const;

    // Генерація UST
    [[nodiscard]] std::vector<std::pair<uint32_t, uint32_t>> generate_ust(uint32_t seed) const;

    // Спектральні характеристики
    [[nodiscard]] SpectralInfo analyze_spectrum() const;

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace graph_walk
