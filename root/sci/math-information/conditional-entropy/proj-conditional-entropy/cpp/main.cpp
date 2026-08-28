#include <iostream>
#include <vector>
#include <cmath>
#include <span>
#include <expected>
#include <string_view>
#include <iomanip>

struct EntropyMetrics {
    double h_x{0.0};          // Ентропія джерела H(X)
    double h_y{0.0};          // Ентропія приймача H(Y)
    double h_xy{0.0};         // Спільна ентропія H(X,Y)
    double h_x_given_y{0.0};    // Умовна ентропія H(X|Y) (equivocation)
    double h_y_given_x{0.0};    // Умовна ентропія H(Y|X)
    double mutual_info{0.0};    // Взаємна інформація I(X;Y)
};

enum class MatrixError {
    InvalidDimensions,
    EmptyData,
    ZeroTotalCount
};

/**
 * Обчислює інформаційні метрики для двовимірної матриці частот.
 * 
 * @param matrix_flat Плоский масив елементів матриці.
 * @param rows Кількість рядків (значень X).
 * @param cols Кількість стовпців (значень Y).
 */
[[nodiscard]] std::expected<EntropyMetrics, MatrixError> 
compute_entropy_metrics(std::span<const double> matrix_flat, size_t rows, size_t cols) {
    if (rows == 0 || cols == 0 || matrix_flat.size() != rows * cols) {
        return std::unexpected(MatrixError::InvalidDimensions);
    }

    double total_count = 0.0;
    for (double val : matrix_flat) {
        total_count += val;
    }

    if (total_count <= 0.0) {
        return std::unexpected(MatrixError::ZeroTotalCount);
    }

    std::vector<double> px(rows, 0.0);
    std::vector<double> py(cols, 0.0);

    for (size_t r = 0; r < rows; ++r) {
        for (size_t c = 0; c < cols; ++c) {
            double p_joint = matrix_flat[r * cols + c] / total_count;
            px[r] += p_joint;
            py[c] += p_joint;
        }
    }

    EntropyMetrics m;

    for (double p : px) {
        if (p > 0.0) {
            m.h_x -= p * std::log2(p);
        }
    }

    for (double p : py) {
        if (p > 0.0) {
            m.h_y -= p * std::log2(p);
        }
    }

    for (size_t r = 0; r < rows; ++r) {
        for (size_t c = 0; c < cols; ++c) {
            double p_joint = matrix_flat[r * cols + c] / total_count;
            if (p_joint > 0.0) {
                m.h_xy -= p_joint * std::log2(p_joint);

                double p_x_given_y = p_joint / py[c];
                m.h_x_given_y -= p_joint * std::log2(p_x_given_y);

                double p_y_given_x = p_joint / px[r];
                m.h_y_given_x -= p_joint * std::log2(p_y_given_x);
            }
        }
    }

    m.mutual_info = m.h_x - m.h_x_given_y;
    return m;
}

int main() {
    // Приклад: BSC з імовірністю помилки p = 0.1 (1000 випробувань)
    std::vector<double> confusion_matrix = {
        450.0,  50.0,
         50.0, 450.0
    };

    auto result = compute_entropy_metrics(confusion_matrix, 2, 2);

    if (result) {
        const auto& m = *result;
        std::cout << std::fixed << std::setprecision(4);
        std::cout << "H(X)     = " << m.h_x << " бітів\n";
        std::cout << "H(Y)     = " << m.h_y << " бітів\n";
        std::cout << "H(X,Y)   = " << m.h_xy << " бітів\n";
        std::cout << "H(X|Y)   = " << m.h_x_given_y << " бітів (equivocation)\n";
        std::cout << "H(Y|X)   = " << m.h_y_given_x << " бітів (шум)\n";
        std::cout << "I(X;Y)   = " << m.mutual_info << " бітів\n";
    } else {
        std::cerr << "Помилка обчислення метрик!\n";
    }

    return 0;
}
