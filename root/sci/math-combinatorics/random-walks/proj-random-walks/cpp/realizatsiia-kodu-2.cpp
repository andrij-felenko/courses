#include <vector>
#include <random>
#include <numeric>
#include <iostream>

class DirectedGraph {
public:
    explicit DirectedGraph(size_t n) : out_adj_(n) {}

    void add_edge(size_t u, size_t v) {
        out_adj_[u].push_back(v);
    }

    [[nodiscard]] size_t size() const noexcept { return out_adj_.size(); }
    [[nodiscard]] const std::vector<size_t>& out_neighbors(size_t u) const { return out_adj_[u]; }

private:
    std::vector<std::vector<size_t>> out_adj_;
};

class PageRankEstimator {
public:
    explicit PageRankEstimator(uint32_t seed = 1337) : rng_(seed) {}

    std::vector<double> estimate(const DirectedGraph& g, double damping = 0.85, 
                                size_t num_walks = 10000, size_t walk_length = 50) {
        const size_t n = g.size();
        std::vector<uint64_t> visits(n, 0);
        uint64_t total_visits = 0;

        std::uniform_int_distribution<size_t> vert_dist(0, n - 1);
        std::uniform_real_distribution<double> prob_dist(0.0, 1.0);

        for (size_t w = 0; w < num_walks; ++w) {
            size_t curr = vert_dist(rng_);
            visits[curr]++;
            total_visits++;

            for (size_t step = 0; step < walk_length; ++step) {
                const auto& neighbors = g.out_neighbors(curr);
                if (prob_dist(rng_) < damping && !neighbors.empty()) {
                    std::uniform_int_distribution<size_t> neigh_dist(0, neighbors.size() - 1);
                    curr = neighbors[neigh_dist(rng_)];
                } else {
                    curr = vert_dist(rng_); // Телепортація
                }
                visits[curr]++;
                total_visits++;
            }
        }

        std::vector<double> rank(n);
        for (size_t i = 0; i < n; ++i) {
            rank[i] = static_cast<double>(visits[i]) / static_cast<double>(total_visits);
        }
        return rank;
    }

private:
    std::mt19937 rng_;
};
