#include <iostream>
#include <vector>
#include <span>
#include <cmath>
#include <iomanip>
#include <expected>
#include <string>

enum class SolverError {
    SingularMatrix,
    DimensionMismatch,
    AllocationFailure
};

class Matrix {
public:
    int rows;
    int cols;
    std::vector<double> data;

    Matrix(int r, int c, double init_val = 0.0)
        : rows(r), cols(c), data(static_cast<size_t>(r * c), init_val) {}

    [[nodiscard]] double& operator()(int r, int c) noexcept {
        return data[static_cast<size_t>(r * cols + c)];
    }

    [[nodiscard]] double operator()(int r, int c) const noexcept {
        return data[static_cast<size_t>(r * cols + c)];
    }

    [[nodiscard]] static Matrix make_hilbert(int n) {
        Matrix H(n, n);
        for (int i = 0; i < n; ++i) {
            for (int j = 0; j < n; ++j) {
                H(i, j) = 1.0 / static_cast<double>(i + j + 1);
            }
        }
        return H;
    }

    [[nodiscard]] double norm_1() const noexcept {
        double max_col = 0.0;
        for (int j = 0; j < cols; ++j) {
            double sum = 0.0;
            for (int i = 0; i < rows; ++i) {
                sum += std::abs((*this)(i, j));
            }
            if (sum > max_col) max_col = sum;
        }
        return max_col;
    }
};

[[nodiscard]] std::vector<double> mat_vec_mul(const Matrix& A, std::span<const double> x) {
    std::vector<double> b(static_cast<size_t>(A.rows), 0.0);
    for (int i = 0; i < A.rows; ++i) {
        for (int j = 0; j < A.cols; ++j) {
            b[static_cast<size_t>(i)] += A(i, j) * x[static_cast<size_t>(j)];
        }
    }
    return b;
}

[[nodiscard]] std::expected<std::vector<double>, SolverError> solve_gauss(
    Matrix A, 
    std::vector<double> b
) {
    const int n = A.rows;
    if (A.cols != n || static_cast<int>(b.size()) != n) {
        return std::unexpected(SolverError::DimensionMismatch);
    }

    for (int k = 0; k < n - 1; ++k) {
        int pivot = k;
        double max_val = std::abs(A(k, k));
        for (int i = k + 1; i < n; ++i) {
            double v = std::abs(A(i, k));
            if (v > max_val) {
                max_val = v;
                pivot = i;
            }
        }

        if (max_val < 1e-15) {
            return std::unexpected(SolverError::SingularMatrix);
        }

        if (pivot != k) {
            for (int j = k; j < n; ++j) {
                std::swap(A(k, j), A(pivot, j));
            }
            std::swap(b[static_cast<size_t>(k)], b[static_cast<size_t>(pivot)]);
        }

        for (int i = k + 1; i < n; ++i) {
            double factor = A(i, k) / A(k, k);
            for (int j = k; j < n; ++j) {
                A(i, j) -= factor * A(k, j);
            }
            b[static_cast<size_t>(i)] -= factor * b[static_cast<size_t>(k)];
        }
    }

    if (std::abs(A(n - 1, n - 1)) < 1e-15) {
        return std::unexpected(SolverError::SingularMatrix);
    }

    std::vector<double> x(static_cast<size_t>(n), 0.0);
    for (int i = n - 1; i >= 0; --i) {
        double sum = 0.0;
        for (int j = i + 1; j < n; ++j) {
            sum += A(i, j) * x[static_cast<size_t>(j)];
        }
        x[static_cast<size_t>(i)] = (b[static_cast<size_t>(i)] - sum) / A(i, i);
    }

    return x;
}

[[nodiscard]] std::expected<std::vector<double>, SolverError> solve_tikhonov(
    const Matrix& A,
    std::span<const double> b,
    double lambda
) {
    const int n = A.cols;
    Matrix AtA(n, n, 0.0);
    std::vector<double> Atb(static_cast<size_t>(n), 0.0);

    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            double sum = 0.0;
            for (int k = 0; k < A.rows; ++k) {
                sum += A(k, i) * A(k, j);
            }
            if (i == j) sum += lambda * lambda;
            AtA(i, j) = sum;
        }
        double b_sum = 0.0;
        for (int k = 0; k < A.rows; ++k) {
            b_sum += A(k, i) * b[static_cast<size_t>(k)];
        }
        Atb[static_cast<size_t>(i)] = b_sum;
    }

    return solve_gauss(std::move(AtA), std::move(Atb));
}

int main() {
    const int n = 6;
    auto H = Matrix::make_hilbert(n);
    std::vector<double> x_exact(static_cast<size_t>(n), 1.0);
    auto b = mat_vec_mul(H, x_exact);

    std::cout << std::scientific << std::setprecision(4);
    std::cout << "Норма ‖H_6‖₁ = " << H.norm_1() << "\n\n";

    auto res_gauss = solve_gauss(H, b);
    if (res_gauss) {
        std::cout << "Розв'язок методом Гаусса:\n";
        for (double v : *res_gauss) std::cout << "  " << v << "\n";
    }

    auto res_tikh = solve_tikhonov(H, b, 1e-4);
    if (res_tikh) {
        std::cout << "\nРозв'язок із регуляризацією Тихонова (λ = 1e-4):\n";
        for (double v : *res_tikh) std::cout << "  " << v << "\n";
    }

    return 0;
}
