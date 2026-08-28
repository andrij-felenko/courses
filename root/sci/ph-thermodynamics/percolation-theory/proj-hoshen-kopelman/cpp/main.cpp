#include <iostream>
#include <vector>
#include <random>
#include <numeric>
#include <algorithm>

// Структура даних Система Неперетинних Множин (Union-Find)
class DisjointSetUnion {
private:
    std::vector<int> parent;
    std::vector<int> rank;

public:
    explicit DisjointSetUnion(int n) : parent(n + 1), rank(n + 1, 0) {
        std::iota(parent.begin(), parent.end(), 0);
    }

    // Пошук кореня з автоматичним стисненням шляху
    int find(int i) {
        if (parent[i] == i)
            return i;
        return parent[i] = find(parent[i]);
    }

    // Об'єднання двох міток за рангом
    void unite(int i, int j) {
        int root_i = find(i);
        int root_j = find(j);
        if (root_i != root_j) {
            if (rank[root_i] < rank[root_j]) {
                std::swap(root_i, root_j);
            }
            parent[root_j] = root_i;
            if (rank[root_i] == rank[root_j]) {
                rank[root_i]++;
            }
        }
    }
};

// Результати аналізу перколаційної сітки
struct PercolationResult {
    bool has_spanning_cluster;
    int total_clusters;
    int max_cluster_size;
    double occupied_fraction;
};

// Клас симуляції узлової перколації на 2D квадратній ґратці
class PercolationSimulation {
private:
    int N;
    double p;
    std::vector<uint8_t> grid; // 1 - відкритий вузол, 0 - закритий

public:
    PercolationSimulation(int size, double prob, uint64_t seed = 42)
        : N(size), p(prob), grid(size * size, 0) {
        
        std::mt19937_64 rng(seed);
        std::bernoulli_distribution dist(p);
        for (int i = 0; i < N * N; ++i) {
            grid[i] = dist(rng) ? 1 : 0;
        }
    }

    PercolationResult run_hoshen_kopelman() {
        std::vector<int> labels(N * N, 0);
        DisjointSetUnion dsu(N * N / 2 + 2);
        int next_label = 1;

        for (int r = 0; r < N; ++r) {
            for (int c = 0; c < N; ++c) {
                int idx = r * N + c;
                if (!grid[idx]) continue;

                int left_label = (c > 0 && grid[idx - 1]) ? labels[idx - 1] : 0;
                int top_label = (r > 0 && grid[idx - N]) ? labels[idx - N] : 0;

                if (left_label == 0 && top_label == 0) {
                    labels[idx] = next_label++;
                } else if (left_label != 0 && top_label == 0) {
                    labels[idx] = left_label;
                } else if (left_label == 0 && top_label != 0) {
                    labels[idx] = top_label;
                } else {
                    labels[idx] = left_label;
                    dsu.unite(left_label, top_label);
                }
            }
        }

        // Другий прохід: нормалізація міток та підрахунок розмірів
        std::vector<int> cluster_sizes(next_label, 0);
        for (int i = 0; i < N * N; ++i) {
            if (labels[i] > 0) {
                labels[i] = dsu.find(labels[i]);
                cluster_sizes[labels[i]]++;
            }
        }

        // Перевірка наскрізного протікання (з верхньої межі до нижньої)
        std::vector<uint8_t> top_roots(next_label, 0);
        std::vector<uint8_t> bottom_roots(next_label, 0);

        for (int c = 0; c < N; ++c) {
            if (labels[c] > 0) top_roots[labels[c]] = 1;
            if (labels[(N - 1) * N + c] > 0) bottom_roots[labels[(N - 1) * N + c]] = 1;
        }

        bool spanning = false;
        int active_clusters = 0;
        int max_size = 0;

        for (int l = 1; l < next_label; ++l) {
            if (cluster_sizes[l] > 0 && dsu.find(l) == l) {
                active_clusters++;
                if (cluster_sizes[l] > max_size) {
                    max_size = cluster_sizes[l];
                }
                if (top_roots[l] && bottom_roots[l]) {
                    spanning = true;
                }
            }
        }

        int occupied_count = 0;
        for (uint8_t cell : grid) occupied_count += cell;

        return {spanning, active_clusters, max_size, static_cast<double>(occupied_count) / (N * N)};
    }
};

int main() {
    const int grid_size = 200;
    const double p_val = 0.59274; // Близько до критичного порогу p_c ≈ 0.592746

    PercolationSimulation sim(grid_size, p_val, 12345);
    PercolationResult res = sim.run_hoshen_kopelman();

    std::cout << "Розмір ґратки: " << grid_size << "x" << grid_size << "\n";
    std::cout << "Частка відкритих вузлів p: " << res.occupied_fraction << "\n";
    std::cout << "Наявність наскрізного кластера: " << (res.has_spanning_cluster ? "ТАК" : "НІ") << "\n";
    std::cout << "Кількість кластерів: " << res.total_clusters << "\n";
    std::cout << "Розмір найбільшого кластера: " << res.max_cluster_size << "\n";

    return 0;
}
