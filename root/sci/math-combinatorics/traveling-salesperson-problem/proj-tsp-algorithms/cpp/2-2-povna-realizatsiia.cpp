#include <vector>
#include <numeric>
#include <algorithm>

/**
 * Обчислення сумарної довжини маршруту на C++.
 */
double calculate_tour_length(const std::vector<size_t>& tour, 
                            const std::vector<std::vector<double>>& matrix) {
    double total = 0.0;
    const size_t n = tour.size();
    for (size_t i = 0; i < n; ++i) {
        total += matrix[tour[i]][tour[(i + 1) % n]];
    }
    return total;
}

/**
 * Ідіоматична C++ реалізація евристики 2-Opt з використанням std::reverse.
 */
void tsp_2opt_refine_cpp(std::vector<size_t>& tour, 
                         const std::vector<std::vector<double>>& matrix) {
    const size_t n = tour.size();
    if (n < 4) return;
    bool improved = true;

    while (improved) {
        improved = false;
        for (size_t i = 0; i < n - 1; ++i) {
            for (size_t j = i + 2; j < n; ++j) {
                if (i == 0 && j == n - 1) continue;

                size_t u = tour[i];
                size_t v = tour[i + 1];
                size_t x = tour[j];
                size_t y = tour[(j + 1) % n];

                double current_dist = matrix[u][v] + matrix[x][y];
                double new_dist = matrix[u][x] + matrix[v][y];

                if (new_dist < current_dist - 1e-9) {
                    /* Ідіоматичний розворот діапазону в C++ */
                    std::reverse(tour.begin() + static_cast<ptrdiff_t>(i + 1), 
                                 tour.begin() + static_cast<ptrdiff_t>(j + 1));
                    improved = true;
                }
            }
        }
    }
}
