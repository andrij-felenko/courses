#include <iostream>
#include <vector>
#include <span>

/* Демонстраційний приклад використання C++20 API */
int run_cpp_api_demo() {
    constexpr int W = 6, H = 6;
    const std::vector<uint8_t> lattice = {
        1, 1, 0, 1, 1, 0,
        1, 0, 0, 0, 1, 0,
        1, 1, 1, 1, 1, 0,
        0, 0, 0, 0, 0, 1,
        0, 1, 1, 0, 0, 1,
        0, 1, 1, 0, 0, 0
    };

    try {
        hoshen_kopelman::GridLabeler2D labeler(W, H,
            hoshen_kopelman::Connectivity::Four,
            hoshen_kopelman::BoundaryCondition::Open);

        std::vector<int> labeled_grid(W * H, 0);

        for (int r = 0; r < H; ++r) {
            std::span<const uint8_t> row_in(&lattice[r * W], W);
            std::span<int> row_out(&labeled_grid[r * W], W);
            labeler.process_row(row_in, row_out);
        }

        labeler.finalize();
        labeler.relabel_grid(labeled_grid);

        auto stats = labeler.get_stats();
        auto sizes = labeler.get_cluster_sizes();

        std::cout << "=== Результати аналізу перколації (C++20) ===\n";
        std::cout << "Кількість кластерів: " << stats.total_clusters << "\n";
        std::cout << "Найбільший кластер:   " << stats.max_cluster_size << "\n";
        std::cout << "Середній розмір S(p): " << stats.mean_cluster_size << "\n";
        std::cout << "Протікання по Y:      " << (stats.has_spanning_cluster_y ? "ТАК" : "НІ") << "\n";

        for (size_t i = 1; i < sizes.size(); ++i) {
            std::cout << "  Кластер #" << i << ": розмір = " << sizes[i] << "\n";
        }
    } catch (const std::exception& ex) {
        std::cerr << "Виник виняток: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
