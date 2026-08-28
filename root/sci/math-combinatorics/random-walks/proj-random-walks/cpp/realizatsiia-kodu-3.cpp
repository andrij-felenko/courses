#include <vector>
#include <random>
#include <unordered_set>
#include <utility>

struct Edge {
    size_t u;
    size_t v;
};

class WilsonUSTGenerator {
public:
    explicit WilsonUSTGenerator(uint32_t seed = 2026) : rng_(seed) {}

    // Генерація рівномірного кістякового дерева за алгоритмом Уїлсона
    std::vector<Edge> generate_ust(const Graph& g) {
        const size_t n = g.num_vertices();
        if (n == 0) return {};

        std::vector<bool> in_tree(n, false);
        std::vector<size_t> next(n, 0);

        // Вершина 0 слугує коренем початкового дерева
        in_tree[0] = true;

        for (size_t i = 1; i < n; ++i) {
            size_t u = i;
            while (!in_tree[u]) {
                const auto& neighbors = g.neighbors(u);
                std::uniform_int_distribution<size_t> dist(0, neighbors.size() - 1);
                size_t v = neighbors[dist(rng_)];
                next[u] = v; // Вилучення циклів відбувається перезаписом next[u]
                u = v;
            }

            u = i;
            while (!in_tree[u]) {
                in_tree[u] = true;
                u = next[u];
            }
        }

        std::vector<Edge> ust;
        ust.reserve(n - 1);
        for (size_t i = 1; i < n; ++i) {
            ust.push_back({i, next[i]});
        }
        return ust;
    }

private:
    std::mt19937 rng_;
};
