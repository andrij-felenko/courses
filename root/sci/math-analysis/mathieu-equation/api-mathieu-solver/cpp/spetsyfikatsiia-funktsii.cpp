// C++20 Інтерфейс класу MathieuSolver у просторі імен mathieu::solver
#include <vector>
#include <array>
#include <expected>

namespace mathieu::solver {

class MathieuSolver {
public:
    explicit MathieuSolver(Config config = {}) : config_(config) {}

    // Обчислення аналізу точки
    [[nodiscard]] PointResult analyze_point(double a, double q) const;

    // Обчислення власних значень a_n(q) та b_n(q)
    [[nodiscard]] double eigenvalue_a(int order_n, double q) const;
    [[nodiscard]] double eigenvalue_b(int order_n, double q) const;

    // Побудова двовимірної сітки стійкості
    [[nodiscard]] Grid compute_grid(
        double q_min, double q_max, std::size_t q_res,
        double a_min, double a_max, std::size_t a_res
    ) const;

    // Показники Флоке та коефіцієнти Фур'є
    [[nodiscard]] std::pair<double, double> floquet_exponents(double a, double q) const;
    [[nodiscard]] std::vector<double> fourier_coefficients(int order_n, double q) const;

private:
    Config config_;
};

} // namespace mathieu::solver
