#include <iostream>
#include <vector>
#include <span>
#include <cmath>
#include <expected>
#include <string_view>

enum class InterpolationError {
    EmptyDataset,
    MismatchedSizes,
    DuplicateNodes
};

/**
 * Обчислення наївної інтерполяції Лагранжа мовою C++20.
 */
[[nodiscard]] std::expected<double, InterpolationError> lagrange_naive_eval(
    std::span<const double> x_nodes, 
    std::span<const double> y_nodes, 
    double target_x) 
{
    if (x_nodes.empty() || y_nodes.empty()) {
        return std::unexpected(InterpolationError::EmptyDataset);
    }
    if (x_nodes.size() != y_nodes.size()) {
        return std::unexpected(InterpolationError::MismatchedSizes);
    }

    const size_t n = x_nodes.size();
    double result = 0.0;

    for (size_t k = 0; k < n; ++k) {
        if (std::abs(target_x - x_nodes[k]) < 1e-12) {
            return y_nodes[k];
        }

        double term = y_nodes[k];
        for (size_t j = 0; j < n; ++j) {
            if (j != k) {
                double denom = x_nodes[k] - x_nodes[j];
                if (std::abs(denom) < 1e-15) {
                    return std::unexpected(InterpolationError::DuplicateNodes);
                }
                term *= (target_x - x_nodes[j]) / denom;
            }
        }
        result += term;
    }

    return result;
}

int main() {
    std::vector<double> x = {1.0, 2.0, 4.0};
    std::vector<double> y = {1.0, 4.0, 16.0};

    double test_x = 3.0;
    auto res = lagrange_naive_eval(x, y, test_x);

    if (res) {
        std::cout << "P(" << test_x << ") = " << *res << " (Очікується: 9.0)\n";
    } else {
        std::cerr << "Помилка обчислення інтерполяції!\n";
    }
    return 0;
}
