#include <concepts>
#include <ranges>
#include <span>
#include <cstdint>
#include <optional>

/* C++20 Concept: вимоги до базового графа */
template <typename G>
concept GraphConcept = requires(const G& g, G& mut_g, uint32_t u, uint32_t v, double w) {
    // Топологічні розміри
    { g.vertex_count() } -> std::same_as<uint32_t>;
    { g.edge_count() }   -> std::same_as<std::size_t>;
    { g.is_directed() }  -> std::same_as<bool>;

    // Запити суміжності
    { g.has_edge(u, v) } -> std::same_as<bool>;
    { g.out_degree(u) }  -> std::same_as<uint32_t>;

    // Діапазон сусідів (forward range або span)
    { g.neighbors(u) }   -> std::ranges::forward_range;

    // Модифікація топології
    { mut_g.add_edge(u, v) } -> std::same_as<bool>;
    { mut_g.remove_edge(u, v) } -> std::same_as<bool>;
};

/* C++20 Concept: розширення для зваженого графа */
template <typename G>
concept WeightedGraphConcept = GraphConcept<G> && requires(const G& g, uint32_t u, uint32_t v) {
    { g.edge_weight(u, v) } -> std::same_as<std::optional<double>>;
};
