// C++ API: Обчислення паросполучення
enum class MatchingAlgorithm {
    Kuhn = 0,
    HopcroftKarp = 1
};

[[nodiscard]] MatchingResult compute_max_matching(
    const BipartiteGraph& graph,
    MatchingAlgorithm algorithm = MatchingAlgorithm::HopcroftKarp
);
