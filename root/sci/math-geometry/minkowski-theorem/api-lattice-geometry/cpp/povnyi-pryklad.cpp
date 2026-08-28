#include <iostream>
#include <vector>
#include <span>
#include <iomanip>
#include <expected>
#include <cmath>

namespace latgeom {

enum class ErrorCode {
    InvalidDimension,
    SingularBasis,
    Timeout,
    NotConvex,
    InvalidParameter
};

struct SvpResult {
    std::vector<int64_t> coordinates;
    std::vector<double> vector;
    double norm{0.0};
    double hermite_factor{0.0};
    uint64_t visited_nodes{0};
};

class LatticeBasis {
public:
    static std::expected<LatticeBasis, ErrorCode> create(size_t dim, std::span<const int64_t> matrix) {
        if (dim == 0 || dim > 64 || matrix.size() != dim * dim) {
            return std::unexpected(ErrorCode::InvalidDimension);
        }
        LatticeBasis basis(dim, matrix);
        if (!basis.orthogonalize()) {
            return std::unexpected(ErrorCode::SingularBasis);
        }
        return basis;
    }

    [[nodiscard]] size_t dimension() const noexcept { return dim_; }
    [[nodiscard]] double determinant() const noexcept { return det_; }
    [[nodiscard]] double log_determinant() const noexcept { return log_det_; }
    [[nodiscard]] double minkowski_radius() const noexcept { return minkowski_radius_; }
    [[nodiscard]] double gaussian_heuristic() const noexcept { return gh_; }
    [[nodiscard]] double orthogonality_defect() const noexcept { return orth_defect_; }

    [[nodiscard]] std::expected<SvpResult, ErrorCode> solve_svp(uint64_t max_nodes = 1'000'000) const {
        double best_sq = minkowski_radius_ * minkowski_radius_;
        std::vector<int64_t> best_z(dim_, 0);
        std::vector<double> best_v(dim_, 0.0);
        uint64_t nodes = 0;

        std::vector<int64_t> cur_z(dim_, 0);
        std::vector<double> cur_l(dim_ + 1, 0.0);

        bool success = enumerate(static_cast<int>(dim_) - 1, cur_z, cur_l,
                                 best_sq, best_z, best_v, nodes, max_nodes);
        if (!success) {
            return std::unexpected(ErrorCode::Timeout);
        }

        double norm = std::sqrt(best_sq);
        double hf = norm / std::pow(det_, 1.0 / static_cast<double>(dim_));

        return SvpResult{
            .coordinates = std::move(best_z),
            .vector = std::move(best_v),
            .norm = norm,
            .hermite_factor = hf,
            .visited_nodes = nodes
        };
    }

private:
    LatticeBasis(size_t dim, std::span<const int64_t> matrix)
        : dim_(dim), b_(matrix.begin(), matrix.end()),
          b_star_(dim * dim, 0.0), mu_(dim * dim, 0.0), b_star_sq_(dim, 0.0) {}

    size_t dim_;
    std::vector<int64_t> b_;
    std::vector<double> b_star_;
    std::vector<double> mu_;
    std::vector<double> b_star_sq_;
    double det_{1.0};
    double log_det_{0.0};
    double minkowski_radius_{0.0};
    double gh_{0.0};
    double orth_defect_{1.0};

    bool orthogonalize() {
        det_ = 1.0;
        log_det_ = 0.0;
        double prod_norms = 1.0;

        for (size_t i = 0; i < dim_; ++i) {
            double orig_sq = 0.0;
            for (size_t j = 0; j < dim_; ++j) {
                b_star_[i * dim_ + j] = static_cast<double>(b_[i * dim_ + j]);
                orig_sq += static_cast<double>(b_[i * dim_ + j]) * static_cast<double>(b_[i * dim_ + j]);
            }
            prod_norms *= std::sqrt(orig_sq);

            for (size_t j = 0; j < i; ++j) {
                double dot = 0.0;
                for (size_t k = 0; k < dim_; ++k) {
                    dot += static_cast<double>(b_[i * dim_ + k]) * b_star_[j * dim_ + k];
                }
                double m = dot / b_star_sq_[j];
                mu_[i * dim_ + j] = m;
                for (size_t k = 0; k < dim_; ++k) {
                    b_star_[i * dim_ + k] -= m * b_star_[j * dim_ + k];
                }
            }
            double sq = 0.0;
            for (size_t k = 0; k < dim_; ++k) {
                sq += b_star_[i * dim_ + k] * b_star_[i * dim_ + k];
            }
            if (sq < 1e-12) return false;
            b_star_sq_[i] = sq;
            det_ *= std::sqrt(sq);
            log_det_ += 0.5 * std::log(sq);
        }
        minkowski_radius_ = std::sqrt(static_cast<double>(dim_)) *
                            std::pow(det_, 1.0 / static_cast<double>(dim_));
        gh_ = std::sqrt(static_cast<double>(dim_) / (2.0 * 3.141592653589793 * 2.718281828459045)) *
              std::pow(det_, 1.0 / static_cast<double>(dim_));
        orth_defect_ = prod_norms / det_;
        return true;
    }

    bool enumerate(int k, std::vector<int64_t>& z, std::vector<double>& l,
                   double& best_sq, std::vector<int64_t>& best_z,
                   std::vector<double>& best_v, uint64_t& nodes, uint64_t max_nodes) const {
        if (++nodes > max_nodes) return false;

        if (k < 0) {
            bool non_zero = false;
            for (int64_t val : z) {
                if (val != 0) { non_zero = true; break; }
            }
            if (non_zero && l[0] < best_sq) {
                best_sq = l[0];
                best_z = z;
                best_v.assign(dim_, 0.0);
                for (size_t j = 0; j < dim_; ++j) {
                    for (size_t i = 0; i < dim_; ++i) {
                        best_v[j] += static_cast<double>(z[i]) * static_cast<double>(b_[i * dim_ + j]);
                    }
                }
            }
            return true;
        }

        double c_k = 0.0;
        for (size_t j = static_cast<size_t>(k) + 1; j < dim_; ++j) {
            c_k -= mu_[j * dim_ + k] * static_cast<double>(z[j]);
        }

        int64_t center_z = static_cast<int64_t>(std::round(c_k));
        int64_t step = 0;

        while (true) {
            int64_t cur_z = 0;
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
            if (!enumerate(k - 1, z, l, best_sq, best_z, best_v, nodes, max_nodes)) {
                return false;
            }
            ++step;
        }
        return true;
    }
};

} // namespace latgeom

int main() {
    constexpr size_t dim = 3;
    const std::vector<int64_t> matrix = {
        5, 2, 1,
        0, 4, 3,
        1, 1, 6
    };

    auto basis_res = latgeom::LatticeBasis::create(dim, matrix);
    if (!basis_res.has_value()) {
        std::cerr << "Не вдалося створити ґратку.\n";
        return 1;
    }

    const auto& basis = *basis_res;
    std::cout << std::fixed << std::setprecision(4);
    std::cout << "=== C++20 інтерфейс liblatgeom ===\n";
    std::cout << "Розмірність простору: " << basis.dimension() << "\n";
    std::cout << "Визначник det(L): " << basis.determinant() << "\n";
    std::cout << "Логарифм визначника: " << basis.log_determinant() << "\n";
    std::cout << "Дефект ортогональності: " << basis.orthogonality_defect() << "\n";
    std::cout << "Радіус Мінковського R_M: " << basis.minkowski_radius() << "\n";
    std::cout << "Гауссова евристика GH(L): " << basis.gaussian_heuristic() << "\n";

    auto svp_res = basis.solve_svp();
    if (svp_res.has_value()) {
        const auto& res = *svp_res;
        std::cout << "\nЗнайдено найкоротший вектор v: [ ";
        for (double val : res.vector) std::cout << val << " ";
        std::cout << "]\n";
        std::cout << "Довжина ||v|| = lambda_1(L): " << res.norm << "\n";
        std::cout << "Фактор Ерміта: " << res.hermite_factor << "\n";
        std::cout << "Перевірка нерівності: " << res.norm << " <= "
                  << basis.minkowski_radius() << " ("
                  << (res.norm <= basis.minkowski_radius() ? "ПІДТВЕРДЖЕНО" : "ПОМИЛКА")
                  << ")\n";
        std::cout << "Відвідано вузлів: " << res.visited_nodes << "\n";
    }

    return 0;
}
