#include "kruskal_api.hpp"
#include <iostream>
#include <vector>

void run_example() {
    std::vector<algorithms::graphs::Edge> edges = {
        {0, 1, 10}, {0, 2, 6}, {0, 3, 5},
        {1, 3, 15}, {2, 3, 4}
    };

    auto result = algorithms::graphs::compute_mst(4, edges);
    if (result.has_value()) {
        std::cout << "Кістяк знайдено, вага: " << result->total_weight << '\n';
    }
}
