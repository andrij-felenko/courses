#include <iostream>
#include <vector>
#include <cmath>
#include <numeric>
#include <optional>
#include <span>
#include <iomanip>

struct SvpResult {
    double norm;
    std::vector<double> vector;
    std::vector<int> coordinates;
    long long visited_nodes;
};

class LatticeSvpSolver {
public:
    explicit LatticeSvpSolver(std::vector<std::vector<double>> basis)
        : n_(basis.size()), b_(std::move(basis)),
          b_star_(n_, std::vector<double>(n_, 0.0)),
          mu_(n_, std::vector<double>(n_, 0.0)),
          b_star_sq_(n_, 0.0) {
        orthogonalize();
    }

    [[nodiscard]] double determinant() const noexcept { return det_; }
    [[nodiscard]] double minkowski_radius() const noexcept { return minkowski_radius_; }
    [[nodiscard]] size_t dimension() const noexcept { return n_; }

    [[nodiscard]] std::optional<SvpResult> solve() const {
        double best_sq = minkowski_radius_ * minkowski_radius_;
        std::vector<int> best_z(n_, 0);
        std::vector<double> best_v(n_, 0.0);
        long long visited_nodes = 0;

        std::vector<int> current_z(n_, 0);
        std::vector<double> current_l(n_ + 1, 0.0);

        enumerate(static_cast<int>(n_) - 1, current_z, current_l,
                  best_sq, best_z, best_v, visited_nodes);

        if (best_sq < minkowski_radius_ * minkowski_radius_) {
            return SvpResult{
                .norm = std::sqrt(best_sq),
                .vector = std::move(best_v),
                .coordinates = std::move(best_z),
                .visited_nodes = visited_nodes
            };
        }
        return std::nullopt;
    }

private:
    size_t n_;
    std::vector<std::vector<double>> b_;
    std::vector<std::vector<double>> b_star_;
    std::vector<std::vector<double>> mu_;
    std::vector<double> b_star_sq_;
    double det_{1.0};
    double minkowski_radius_{0.0};

    static double dot(std::span<const double> u, std::span<const double> v) noexcept {
        double s = 0.0;
        for (size_t i = 0; i < u.size(); ++i) s += u[i] * v[i];
        return s;
    }

    void orthogonalize() {
        det_ = 1.0;
        for (size_t i = 0; i < n_; ++i) {
            b_star_[i] = b_[i];
            for (size_t j = 0; j < i; ++j) {
                double num = dot(b_[i], b_star_[j]);
                mu_[i][j] = num / b_star_sq_[j];
                for (size_t k = 0; k < n_; ++k) {
                    b_star_[i][k] -= mu_[i][j] * b_star_[j][k];
                }
            }
            b_star_sq_[i] = dot(b_star_[i], b_star_[i]);
            det_ *= std::sqrt(b_star_sq_[i]);
        }
        minkowski_radius_ = std::sqrt(static_cast<double>(n_)) *
                            std::pow(det_, 1.0 / static_cast<double>(n_));
    }

    void enumerate(int k, std::vector<int>& z, std::vector<double>& l,
                   double& best_sq, std::vector<int>& best_z,
                   std::vector<double>& best_v, long long& nodes) const {
        ++nodes;

        if (k < 0) {
            bool non_zero = false;
            for (int val : z) {
                if (val != 0) { non_zero = true; break; }
            }
            if (non_zero && l[0] < best_sq) {
                best_sq = l[0];
                best_z = z;
                best_v.assign(n_, 0.0);
                for (size_t j = 0; j < n_; ++j) {
                    for (size_t i = 0; i < n_; ++i) {
                        best_v[j] += static_cast<double>(z[i]) * b_[i][j];
                    }
                }
            }
            return;
        }

        double c_k = 0.0;
        for (size_t j = static_cast<size_t>(k) + 1; j < n_; ++j) {
            c_k -= mu_[j][k] * static_cast<double>(z[j]);
        }

        int center_z = static_cast<int>(std::round(c_k));
        int step = 0;

        while (true) {
            int cur_z = 0;
            if (step == 0) cur_z = center_z;
            else if (step % 2 == 1) cur_z = center_z + (step + 1) / 2;
            else cur_z = center_z - step / 2;

            double diff = static_cast<double>(cur_z) - c_k;
            double new_l = l[k + 1] + diff * diff * b_star_sq_[k];

            if (new_l >= best_sq) {
                if (step > 1) break;
                ++step;
                continue;
            }

            z[k] = cur_z;
            l[k] = new_l;
            enumerate(k - 1, z, l, best_sq, best_z, best_v, nodes);
            ++step;
        }
    }
};

int main() {
    std::vector<std::vector<double>> basis = {
        { 17.0,  0.0,  0.0,  0.0 },
        {  3.0,  1.0,  0.0,  0.0 },
        {  7.0,  0.0,  1.0,  0.0 },
        {  5.0,  0.0,  0.0,  1.0 }
    };

    LatticeSvpSolver solver(std::move(basis));
    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=== C++ перевірка теореми Мінковського для ґратки в R^4 ===\n";
    std::cout << "Визначник ґратки det(L): " << solver.determinant() << "\n";
    std::cout << "Теоретична межа Мінковського R_M: " << solver.minkowski_radius() << "\n";

    if (auto res = solver.solve()) {
        std::cout << "Знайдено найкоротший вектор v: [ ";
        for (double x : res->vector) std::cout << x << " ";
        std::cout << "]\n";
        std::cout << "Фактична довжина ||v|| = lambda_1(L): " << res->norm << "\n";
        std::cout << "Нерівність Мінковського (lambda_1 <= R_M): " << res->norm << " <= "
                  << solver.minkowski_radius() << " ("
                  << (res->norm <= solver.minkowski_radius() ? "ПІДТВЕРДЖЕНО" : "ПОМИЛКА")
                  << ")\n";
        std::cout << "Кількість відвіданих вузлів дерева: " << res->visited_nodes << "\n";
    } else {
        std::cout << "Помилка: вектор не знайдено в кулі Мінковського.\n";
    }

    return 0;
}
