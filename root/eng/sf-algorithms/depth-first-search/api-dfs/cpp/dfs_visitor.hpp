// C++ API (dfs_visitor.hpp) — шаблон з C++20 концептами
#ifndef DFS_VISITOR_HPP
#define DFS_VISITOR_HPP

#include <vector>
#include <concepts>
#include <cstddef>
#include <cstdint>
#include <utility>

namespace algo {

struct default_dfs_visitor {
    void initialize_vertex(int /*u*/) noexcept {}
    void start_vertex(int /*u*/) noexcept {}
    void discover_vertex(int /*u*/, int /*d_time*/) noexcept {}
    void examine_edge(int /*u*/, int /*v*/) noexcept {}
    void tree_edge(int /*u*/, int /*v*/) noexcept {}
    void back_edge(int /*u*/, int /*v*/) noexcept {}
    void forward_or_cross_edge(int /*u*/, int /*v*/) noexcept {}
    void finish_edge(int /*u*/, int /*v*/) noexcept {}
    void finish_vertex(int /*u*/, int /*f_time*/) noexcept {}
};

template <typename V>
concept DFSVisitor = requires(V v, int u, int target, int time) {
    { v.initialize_vertex(u) };
    { v.start_vertex(u) };
    { v.discover_vertex(u, time) };
    { v.examine_edge(u, target) };
    { v.tree_edge(u, target) };
    { v.back_edge(u, target) };
    { v.forward_or_cross_edge(u, target) };
    { v.finish_edge(u, target) };
    { v.finish_vertex(u, time) };
};

enum class Color : std::uint8_t { White, Gray, Black };

template <typename Graph, DFSVisitor Visitor>
class DFSEngine {
public:
    static void run(const Graph& g, Visitor visitor) {
        const std::size_t n = g.num_vertices();
        std::vector<Color> color(n, Color::White);
        std::vector<int> discovery_time(n, 0);
        std::vector<int> finish_time(n, 0);
        int timer = 0;

        for (std::size_t u = 0; u < n; ++u) {
            visitor.initialize_vertex(static_cast<int>(u));
        }

        auto visit = [&](auto& self, int u) -> void {
            color[u] = Color::Gray;
            discovery_time[u] = ++timer;
            visitor.discover_vertex(u, discovery_time[u]);

            for (int v : g.neighbors(u)) {
                visitor.examine_edge(u, v);

                if (color[v] == Color::White) {
                    visitor.tree_edge(u, v);
                    self(self, v);
                    visitor.finish_edge(u, v);
                } else if (color[v] == Color::Gray) {
                    visitor.back_edge(u, v);
                } else {
                    visitor.forward_or_cross_edge(u, v);
                }
            }

            color[u] = Color::Black;
            finish_time[u] = ++timer;
            visitor.finish_vertex(u, finish_time[u]);
        };

        for (std::size_t u = 0; u < n; ++u) {
            if (color[u] == Color::White) {
                visitor.start_vertex(static_cast<int>(u));
                visit(visit, static_cast<int>(u));
            }
        }
    }
};

template <typename Graph, typename Visitor>
void depth_first_search(const Graph& g, Visitor&& visitor) {
    DFSEngine<Graph, std::decay_t<Visitor>>::run(g, std::forward<Visitor>(visitor));
}

} // namespace algo

#endif // DFS_VISITOR_HPP
