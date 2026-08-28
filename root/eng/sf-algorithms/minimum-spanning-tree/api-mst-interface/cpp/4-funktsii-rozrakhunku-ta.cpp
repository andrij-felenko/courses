namespace mst {

class Solver {
public:
    [[nodiscard]] static std::expected<Solution, StatusCode> solve(
        const Graph& graph,
        AlgorithmType algo = AlgorithmType::Auto
    );

    [[nodiscard]] static bool verify_solution(
        size_t num_vertices,
        const Solution& solution
    ) noexcept;
};

} // namespace mst
