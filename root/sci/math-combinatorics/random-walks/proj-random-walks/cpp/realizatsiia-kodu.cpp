#include <vector>
#include <random>
#include <iostream>
#include <cstdint>

class Graph {
public:
    explicit Graph(size_t vertices) : adj_(vertices) {}

    void add_edge(size_t u, size_t v) {
        adj_[u].push_back(v);
        adj_[v].push_back(u);
        num_edges_++;
    }

    [[nodiscard]] size_t num_vertices() const noexcept { return adj_.size(); }
    [[nodiscard]] size_t num_edges() const noexcept { return num_edges_; }
    [[nodiscard]] const std::vector<size_t>& neighbors(size_t u) const { return adj_[u]; }

private:
    std::vector<std::vector<size_t>> adj_;
    size_t num_edges_{0};
};

class RandomWalkChecker {
public:
    explicit RandomWalkChecker(uint32_t seed = 42) : rng_(seed) {}

    // Перевірка s-t зв'язності з мінімальним споживанням пам'яті
    bool check_st_connectivity(const Graph& g, size_t s, size_t t, size_t max_runs = 5) {
        if (s == t) return true;
        if (g.neighbors(s).empty() || g.neighbors(t).empty()) return false;

        const uint64_t max_steps = 2ULL * g.num_edges() * g.num_vertices();

        for (size_t run = 0; run < max_runs; ++run) {
            size_t current = s;
            for (uint64_t step = 0; step < max_steps; ++step) {
                const auto& neighbors = g.neighbors(current);
                std::uniform_int_distribution<size_t> dist(0, neighbors.size() - 1);
                current = neighbors[dist(rng_)];

                if (current == t) {
                    return true;
                }
            }
        }
        return false;
    }

private:
    std::mt19937 rng_;
};
