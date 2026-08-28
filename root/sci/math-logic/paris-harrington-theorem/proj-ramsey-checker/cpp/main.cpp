#include <iostream>
#include <vector>
#include <optional>
#include <cstdint>

class ParisHarringtonVerifier {
public:
    explicit ParisHarringtonVerifier(int dimension, int target_m, int num_colors)
        : n_(dimension), m_(target_m), c_(num_colors) {}

    // Перевіряє, чи є підмножина вузлів великою та монохроматичною
    [[nodiscard]] bool is_large_monochromatic(
        const std::vector<int>& coloring,
        int n_nodes,
        uint32_t mask
    ) const {
        int count = 0;
        int min_val = n_nodes + 1;

        for (int i = 0; i < n_nodes; ++i) {
            if ((mask >> i) & 1) {
                count++;
                int val = i + 1;
                if (val < min_val) {
                    min_val = val;
                }
            }
        }

        if (count < m_ || count < min_val) {
            return false;
        }

        int target_color = -1;
        for (int i = 0; i < n_nodes; ++i) {
            if (!((mask >> i) & 1)) continue;
            for (int j = i + 1; j < n_nodes; ++j) {
                if (!((mask >> j) & 1)) continue;

                int edge_idx = i * n_nodes + j;
                int col = coloring[edge_idx];
                if (target_color == -1) {
                    target_color = col;
                } else if (target_color != col) {
                    return false;
                }
            }
        }
        return true;
    }

    // Шукає контрприклад (погане розфарбування) для даного N
    [[nodiscard]] bool has_bad_coloring(int n_nodes) const {
        std::vector<int> coloring(n_nodes * n_nodes, 0);
        return search_bad(coloring, n_nodes, 0, 1);
    }

    // Знаходить число PH(2, m, c)
    [[nodiscard]] std::optional<int> compute_ph_bound(int max_search_n) const {
        for (int N = m_; N <= max_search_n; ++N) {
            if (!has_bad_coloring(N)) {
                return N;
            }
        }
        return std::nullopt;
    }

private:
    bool has_any_large_mono(const std::vector<int>& coloring, int n_nodes) const {
        uint32_t total_subsets = 1U << n_nodes;
        for (uint32_t mask = 1; mask < total_subsets; ++mask) {
            if (is_large_monochromatic(coloring, n_nodes, mask)) {
                return true;
            }
        }
        return false;
    }

    bool search_bad(std::vector<int>& coloring, int n_nodes, int u, int v) const {
        if (u >= n_nodes - 1) {
            return !has_any_large_mono(coloring, n_nodes);
        }

        int next_u = u;
        int next_v = v + 1;
        if (next_v >= n_nodes) {
            next_u = u + 1;
            next_v = next_u + 1;
        }

        for (int color = 0; color < c_; ++color) {
            coloring[u * n_nodes + v] = color;
            coloring[v * n_nodes + u] = color;

            if (search_bad(coloring, n_nodes, next_u, next_v)) {
                return true;
            }
        }
        return false;
    }

    int n_;
    int m_;
    int c_;
};

int main() {
    std::cout << "Обчислення числа Паріса — Гаррінгтона PH(2, 3, 2) мовою C++:\n";
    ParisHarringtonVerifier verifier(2, 3, 2);

    auto result = verifier.compute_ph_bound(15);
    if (result.has_value()) {
        std::cout << "Успішно знайдено поріг: PH(2, 3, 2) = " << result.value() << "\n";
    } else {
        std::cout << "Поріг не знайдено у межах пошуку.\n";
    }

    return 0;
}
