#include <iostream>
#include <vector>
#include <bitset>
#include <optional>
#include <cstdint>
#include <numeric>
#include <array>
#include <bit>

namespace ramsey {

template <std::size_t N>
class graph_coloring {
public:
    static_assert(N <= 64, "Класова реалізація обмежена 64 вершинами для швидкодії бітових масок");

    graph_coloring() : num_vertices_(N) {
        adj_red_.fill(0);
    }

    explicit graph_coloring(std::size_t n) : num_vertices_(n) {
        adj_red_.fill(0);
    }

    [[nodiscard]] std::size_t size() const noexcept { return num_vertices_; }

    void set_edge(std::size_t u, std::size_t v, bool is_red) noexcept {
        if (is_red) {
            adj_red_[u] |= (1ULL << v);
            adj_red_[v] |= (1ULL << u);
        } else {
            adj_red_[u] &= ~(1ULL << v);
            adj_red_[v] &= ~(1ULL << u);
        }
    }

    [[nodiscard]] bool get_edge(std::size_t u, std::size_t v) const noexcept {
        return (adj_red_[u] & (1ULL << v)) != 0;
    }

    [[nodiscard]] std::uint64_t red_neighbors(std::size_t v) const noexcept {
        return adj_red_[v];
    }

    [[nodiscard]] std::uint64_t blue_neighbors(std::size_t v) const noexcept {
        uint64_t mask = (num_vertices_ == 64) ? ~0ULL : ((1ULL << num_vertices_) - 1);
        return (~adj_red_[v]) & mask & ~(1ULL << v);
    }

    [[nodiscard]] bool has_monochromatic_clique(std::size_t r, std::size_t s) const {
        uint64_t all_v = (num_vertices_ == 64) ? ~0ULL : ((1ULL << num_vertices_) - 1);
        return check_clique(all_v, r, 0, true) || check_clique(all_v, s, 0, false);
    }

private:
    std::size_t num_vertices_;
    std::array<std::uint64_t, N> adj_red_{};

    bool check_clique(std::uint64_t candidates, std::size_t target_size, std::size_t current_size, bool is_red) const {
        if (current_size == target_size) {
            return true;
        }

        while (candidates > 0) {
            int popcnt = std::popcount(candidates);
            if (current_size + static_cast<std::size_t>(popcnt) < target_size) {
                return false;
            }

            int v = std::countr_zero(candidates);
            candidates &= ~(1ULL << v);

            std::uint64_t neighbors = is_red ? red_neighbors(v) : blue_neighbors(v);
            std::uint64_t mask_future = ~((1ULL << (v + 1)) - 1);
            std::uint64_t next_candidates = candidates & neighbors & mask_future;

            if (check_clique(next_candidates, target_size, current_size + 1, is_red)) {
                return true;
            }
        }
        return false;
    }
};

template <std::size_t N>
class solver {
public:
    static std::optional<graph_coloring<N>> find_counterexample(std::size_t r, std::size_t s) {
        graph_coloring<N> g;
        std::vector<std::pair<std::size_t, std::size_t>> edges;
        for (std::size_t i = 0; i < N; ++i) {
            for (std::size_t j = i + 1; j < N; ++j) {
                edges.emplace_back(i, j);
            }
        }

        if (search(g, 0, edges, r, s)) {
            return g;
        }
        return std::nullopt;
    }

private:
    static bool search(graph_coloring<N>& g, std::size_t edge_idx,
                       const std::vector<std::pair<std::size_t, std::size_t>>& edges,
                       std::size_t r, std::size_t s) {
        if (edge_idx == edges.size()) {
            return !g.has_monochromatic_clique(r, s);
        }

        auto [u, v] = edges[edge_idx];

        // Спроба червоного ребра
        g.set_edge(u, v, true);
        if (search(g, edge_idx + 1, edges, r, s)) {
            return true;
        }

        // Спроба синього ребра
        g.set_edge(u, v, false);
        if (search(g, edge_idx + 1, edges, r, s)) {
            return true;
        }

        return false;
    }
};

} // namespace ramsey

int main() {
    std::cout << "=== Перевірка чисел Рамсея (C++20 Implementation) ===\n";
    constexpr std::size_t r = 3, s = 3;

    // Перевіряємо гранули від n = 3 до 6
    auto run_check = []<std::size_t N>() {
        auto result = ramsey::solver<N>::find_counterexample(r, s);
        if (result.has_value()) {
            std::cout << "n = " << N << ": Знайдено контрприклад! R(" << r << ", " << s << ") > " << N << "\n";
        } else {
            std::cout << "n = " << N << ": Не існує контрприкладу. Отже R(" << r << ", " << s << ") <= " << N << "\n";
        }
    };

    run_check.operator()<3>();
    run_check.operator()<4>();
    run_check.operator()<5>();
    run_check.operator()<6>();

    return 0;
}
