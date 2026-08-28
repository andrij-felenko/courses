#include "takens.hpp"
#include <iostream>
#include <vector>

void run_mi_example_cpp(const std::vector<double>& signal) {
    takens::Config config;
    config.max_delay = 40;

    auto result = takens::compute_mutual_information(signal, config);
    if (result.has_value()) {
        std::cout << "Оптимальна затримка tau: " << result->optimal_delay << " відліків\n";
    } else {
        std::cerr << "Помилка обчислення MI\n";
    }
}
