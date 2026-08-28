#include <vector>
#include <memory>
#include <span >
#include <string_view>
#include <expected>
#include <system_error>

namespace scc {

/* Інформація про одну компоненту сильної зв'язаності */
struct ComponentInfo {
    int id{0};
    std::vector<int> members;
};

/* Результат обчислення та аналізу графа у C++20 */
struct AnalysisResult {
    int vertex_count{0};
    int component_count{0};
    std::vector<int> component_map;                 // comp_map[u] -> scc_id
    std::vector<ComponentInfo> components;          // scc_id -> ComponentInfo
    std::vector<std::vector<int>> condensation_dag; // scc_id -> list of adjacent scc_ids

    /* Перевірка взаємної досяжності двох вершин за O(1) */
    [[nodiscard]] bool are_mutually_reachable(int u, int v) const noexcept {
        if (u < 0 || u >= vertex_count || v < 0 || v >= vertex_count) return false;
        return component_map[u] == component_map[v];
    }
};

/* Конфігураційні налаштування аналізатора C++ */
struct AnalyzerConfig {
    bool build_condensation{true};
    bool validate_inputs{true};
    size_t initial_buffer_size{1024};
};

} // namespace scc
