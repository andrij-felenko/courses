// C++ API: Результат 2-розфарбовування
namespace net {

struct PartitionResult {
    bool is_bipartite{true};
    std::vector<int> colors; // Колір 0 (частка U), 1 (частка V)
    std::optional<std::pair<std::size_t, std::size_t>> conflict_edge;
    std::vector<std::size_t> odd_cycle;
};

} // namespace net
