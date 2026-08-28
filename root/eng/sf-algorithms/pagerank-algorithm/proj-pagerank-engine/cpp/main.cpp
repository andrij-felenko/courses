#include <vector>
#include <cmath>
#include <span>
#include <memory>
#include <expected>
#include <string>
#include <numeric>
#include <algorithm>

// Клас розрідженого графа у форматі CSR
class CsrGraph {
public:
    int num_nodes = 0;
    int num_edges = 0;
    std::vector<int> row_ptr;     // розмір num_nodes + 1
    std::vector<int> col_idx;     // розмір num_edges
    std::vector<int> out_degree;  // розмір num_nodes

    CsrGraph(int nodes, int edges)
        : num_nodes(nodes),
          num_edges(edges),
          row_ptr(nodes + 1, 0),
          col_idx(edges, 0),
          out_degree(nodes, 0) {}
};

// Результат обчислення
struct PageRankResult {
    std::vector<double> ranks;
    int iterations = 0;
    double final_diff = 0.0;
    bool converged = false;
};

// Обчислення PageRank
std::expected<PageRankResult, std::string> compute_pagerank(
    const CsrGraph& graph,
    double damping = 0.85,
    double tolerance = 1e-7,
    int max_iterations = 100)
{
    const int N = graph.num_nodes;
    if (N <= 0) {
        return std::unexpected("Кількість вершин у графі повинна бути більше нуля");
    }

    PageRankResult result;
    result.ranks.assign(N, 1.0 / static_cast<double>(N));
    std::vector<double> r_next(N, 0.0);

    int iter = 0;
    double diff = 0.0;

    while (iter < max_iterations) {
        iter++;

        // 1. Акумуляція рангу висячих вузлів (out_degree == 0)
        double dangling_sum = 0.0;
        for (int u = 0; u < N; ++u) {
            if (graph.out_degree[u] == 0) {
                dangling_sum += result.ranks[u];
            }
        }

        // 2. Базовий рівномірний внесок телепортації для кожної вершини
        const double base_rank = (damping * dangling_sum + (1.0 - damping)) / static_cast<double>(N);
        std::fill(r_next.begin(), r_next.end(), base_rank);

        // 3. Розподіл рангу вздовж орієнтованих ребер u -> v
        for (int u = 0; u < N; ++u) {
            const int deg = graph.out_degree[u];
            if (deg > 0) {
                const double share = (damping * result.ranks[u]) / static_cast<double>(deg);
                const int start = graph.row_ptr[u];
                const int end = graph.row_ptr[u + 1];
                for (int e = start; e < end; ++e) {
                    const int v = graph.col_idx[e];
                    r_next[v] += share;
                }
            }
        }

        // 4. Оцінка похибки за L1-нормою: sum |r_next[i] - r_cur[i]|
        diff = 0.0;
        for (int i = 0; i < N; ++i) {
            diff += std::abs(r_next[i] - result.ranks[i]);
            result.ranks[i] = r_next[i];
        }

        if (diff < tolerance) {
            result.converged = true;
            break;
        }
    }

    result.iterations = iter;
    result.final_diff = diff;
    return result;
}
