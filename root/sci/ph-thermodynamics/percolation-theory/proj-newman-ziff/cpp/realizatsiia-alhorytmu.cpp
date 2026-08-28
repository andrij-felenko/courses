#include <iostream>
#include <vector>
#include <numeric>
#include <random>
#include <cmath>
#include <cstdint>
#include <algorithm>
#include <span>

class NewmanZiffSimulation {
public:
    static constexpr int EMPTY = -2000000000;

    explicit NewmanZiffSimulation(int side_length)
        : L(side_length), N(side_length * side_length),
          parent(N, EMPTY), mask(N, 0), order(N), s_max(N + 1, 0) {
        std::iota(order.begin(), order.end(), 0);
        std::random_device rd;
        std::mt19937_64 rng(rd());
        std::shuffle(order.begin(), order.end(), rng);
    }

    int find_root(int i) {
        if (parent[i] < 0) return i;
        return parent[i] = find_root(parent[i]);
    }

    int union_sets(int r1, int r2) {
        if (r1 == r2) return r1;

        if (parent[r1] > parent[r2]) {
            std::swap(r1, r2);
        }

        parent[r1] += parent[r2];
        parent[r2] = r1;
        mask[r1] |= mask[r2];

        if (!has_percolated && (mask[r1] & 0x03) == 0x03) {
            has_percolated = true;
        }

        return r1;
    }

    void run() {
        int max_cluster = 0;
        constexpr int dx[4] = {0, 0, -1, 1};
        constexpr int dy[4] = {-1, 1, 0, 0};

        for (int step = 1; step <= N; ++step) {
            int site = order[step - 1];
            int x = site % L;
            int y = site / L;

            parent[site] = -1;
            uint8_t m = 0;
            if (y == 0)     m |= 0x01;
            if (y == L - 1) m |= 0x02;
            if (x == 0)     m |= 0x04;
            if (x == L - 1) m |= 0x08;
            mask[site] = m;

            int root = site;
            if (max_cluster < 1) max_cluster = 1;

            for (int k = 0; k < 4; ++k) {
                int nx = x + dx[k];
                int ny = y + dy[k];

                if (nx >= 0 && nx < L && ny >= 0 && ny < L) {
                    int n_idx = ny * L + nx;
                    if (parent[n_idx] != EMPTY) {
                        int n_root = find_root(n_idx);
                        if (n_root != root) {
                            root = union_sets(root, n_root);
                        }
                    }
                }
            }

            int cur_size = -parent[root];
            if (cur_size > max_cluster) {
                max_cluster = cur_size;
            }

            s_max[step] = max_cluster;

            if (has_percolated && percolation_step == -1) {
                percolation_step = step;
            }
        }
    }

    [[nodiscard]] double compute_canonical_p_inf(double p) const {
        if (p <= 0.0) return 0.0;
        if (p >= 1.0) return 1.0;

        const double log_p = std::log(p);
        const double log_1_p = std::log(1.0 - p);

        const int n_mode = std::clamp(static_cast<int>(N * p), 0, N);
        const double sigma = std::sqrt(N * p * (1.0 - p));
        const int n_min = std::max(0, static_cast<int>(n_mode - 6.0 * sigma));
        const int n_max = std::min(N, static_cast<int>(n_mode + 6.0 * sigma));

        auto log_comb = [this](int n) {
            double res = 0.0;
            int k = std::min(n, N - n);
            for (int i = 1; i <= k; ++i) {
                res += std::log(static_cast<double>(N - i + 1) / static_cast<double>(i));
            }
            return res;
        };

        const double log_mode_weight = log_comb(n_mode) + n_mode * log_p + (N - n_mode) * log_1_p;

        double weighted_sum = 0.0;
        double norm = 0.0;

        for (int n = n_min; n <= n_max; ++n) {
            double log_w = log_comb(n) + n * log_p + (N - n) * log_1_p - log_mode_weight;
            double w = std::exp(log_w);
            weighted_sum += static_cast<double>(s_max[n]) * w;
            norm += w;
        }

        return (norm > 0.0) ? (weighted_sum / norm) / static_cast<double>(N) : 0.0;
    }

    [[nodiscard]] int get_percolation_step() const noexcept { return percolation_step; }
    [[nodiscard]] double get_critical_density() const noexcept {
        return static_cast<double>(percolation_step) / static_cast<double>(N);
    }

private:
    int L;
    int N;
    std::vector<int> parent;
    std::vector<uint8_t> mask;
    std::vector<int> order;
    std::vector<int> s_max;
    bool has_percolated{false};
    int percolation_step{-1};
};
