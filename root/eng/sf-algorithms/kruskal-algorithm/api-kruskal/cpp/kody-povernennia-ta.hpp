#ifndef KRUSKAL_API_HPP
#define KRUSKAL_API_HPP

#include <cstdint>
#include <cstddef>
#include <span>
#include <vector>
#include <expected>

namespace algorithms::graphs {

// Компактне представлення ребра з підтримкою операцій порівняння
struct Edge {
    uint32_t u{0};
    uint32_t v{0};
    int64_t weight{0};

    [[nodiscard]] constexpr bool operator==(const Edge&) const noexcept = default;
    [[nodiscard]] constexpr bool operator<(const Edge& other) const noexcept {
        return weight < other.weight;
    }
};

// Типізовані коди помилок
enum class ErrorCode {
    InvalidVertexIndex,
    EmptyGraph,
    AllocationFailure
};

// Результат побудови кістяка з автоматичним керуванням пам'яттю
struct MstResult {
    std::vector<Edge> edges;
    int64_t total_weight{0};
    uint32_t num_components{1};
    bool is_fully_connected{true};
};

/**
 * @brief Знаходить мінімальне кістякове дерево на множині ребер.
 * 
 * @param num_vertices Загальна кількість вершин графа (індекси від 0 до num_vertices - 1).
 * @param edges        Вхідний зріз ребер. Сортується безпосередньо за місцем (in-place).
 * 
 * @return std::expected<MstResult, ErrorCode> Результат або код помилки.
 */
[[nodiscard]] std::expected<MstResult, ErrorCode>
compute_mst(uint32_t num_vertices, std::span<Edge> edges);

} // namespace algorithms::graphs

#endif // KRUSKAL_API_HPP
