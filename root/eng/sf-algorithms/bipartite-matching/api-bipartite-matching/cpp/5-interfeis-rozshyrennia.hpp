// C++20 API для Угорського алгоритму
namespace graph::matching {

template <typename WeightType = double>
struct WeightedEdge {
    std::size_t u;
    std::size_t v;
    WeightType weight;
};

template <typename WeightType = double>
struct WeightedMatchingSolution {
    WeightType total_weight{0};
    std::vector<WeightedEdge<WeightType>> matched_edges;
};

template <typename WeightType = double>
class HungarianSolver {
public:
    explicit HungarianSolver(const std::vector<std::vector<WeightType>>& weight_matrix);

    [[nodiscard]] WeightedMatchingSolution<WeightType> solve_max_weight();
    [[nodiscard]] WeightedMatchingSolution<WeightType> solve_min_weight();
};

} // namespace graph::matching
