#include <iostream>
#include <vector>
#include <array>
#include <cmath>
#include <iomanip>
#include <numeric>
#include <algorithm>

namespace rtk {

template <size_t N>
struct LambdaResult {
    std::array<int64_t, N> fix1{};
    std::array<int64_t, N> fix2{};
    double f1{0.0};
    double f2{0.0};
    double ratio{0.0};
    bool is_fixed{false};
};

template <size_t N>
class LambdaSolver {
public:
    using Matrix = std::array<std::array<double, N>, N>;
    using Vector = std::array<double, N>;

    LambdaResult<N> solve(const Vector& a_hat, const Matrix& Q_a, double ratio_thresh = 2.5) {
        Matrix L{};
        Vector D{};
        Matrix Z{};

        factorize_ldl(Q_a, L, D);
        reduce_lattice(L, D, Z);

        // ẑ = Zᵀ · â
        Vector z_hat{};
        for (size_t i = 0; i < N; ++i) {
            for (size_t j = 0; j < N; ++j) {
                z_hat[i] += Z[j][i] * a_hat[j];
            }
        }

        Vector z_fix1{}, z_fix2{};
        double f1{1e9}, f2{1e9};
        search_tree(L, D, z_hat, z_fix1, z_fix2, f1, f2);

        LambdaResult<N> result;
        result.f1 = f1;
        result.f2 = f2;
        result.ratio = (f1 > 1e-12) ? (f2 / f1) : 999.0;
        result.is_fixed = (result.ratio >= ratio_thresh);

        // Зворотне перетворення: ǎ = Z · ž
        for (size_t i = 0; i < N; ++i) {
            double val1 = 0.0, val2 = 0.0;
            for (size_t j = 0; j < N; ++j) {
                val1 += Z[i][j] * z_fix1[j];
                val2 += Z[i][j] * z_fix2[j];
            }
            result.fix1[i] = static_cast<int64_t>(std::round(val1));
            result.fix2[i] = static_cast<int64_t>(std::round(val2));
        }

        return result;
    }

private:
    void factorize_ldl(const Matrix& Q, Matrix& L, Vector& D) {
        for (size_t i = 0; i < N; ++i) {
            for (size_t j = 0; j < N; ++j) {
                L[i][j] = (i == j) ? 1.0 : 0.0;
            }
            D[i] = 0.0;
        }

        for (int i = static_cast<int>(N) - 1; i >= 0; --i) {
            D[i] = Q[i][i];
            for (size_t j = i + 1; j < N; ++j) {
                double lij = L[j][i];
                D[i] -= lij * lij * D[j];
            }
            if (D[i] <= 0.0) D[i] = 1e-12;

            for (int j = 0; j < i; ++j) {
                double sum = Q[i][j];
                for (size_t k = i + 1; k < N; ++k) {
                    sum -= L[k][i] * L[k][j] * D[k];
                }
                L[i][j] = sum / D[i];
            }
        }
    }

    void gauss_transform(Matrix& L, Matrix& Z, size_t i, size_t j) {
        int mu = static_cast<int>(std::round(L[i][j]));
        if (mu == 0) return;

        for (size_t k = i; k < N; ++k) {
            L[k][j] -= static_cast<double>(mu) * L[k][i];
        }
        for (size_t k = 0; k < N; ++k) {
            Z[k][j] -= static_cast<double>(mu) * Z[k][i];
        }
    }

    void swap_coordinates(Matrix& L, Vector& D, Matrix& Z, size_t i) {
        size_t j = i + 1;
        double d1 = D[i], d2 = D[j];
        double lambda = L[j][i];
        double delta = d1 + lambda * lambda * d2;

        D[i] = delta;
        D[j] = (d1 * d2) / delta;
        L[j][i] = (lambda * d2) / delta;

        for (size_t k = 0; k < i; ++k) {
            std::swap(L[i][k], L[j][k]);
        }
        for (size_t k = j + 1; k < N; ++k) {
            double lki = L[k][i];
            double lkj = L[k][j];
            L[k][i] = lki * L[j][i] + lkj * (d2 / delta);
            L[k][j] = lki - lkj * lambda;
        }
        for (size_t k = 0; k < N; ++k) {
            std::swap(Z[k][i], Z[k][j]);
        }
    }

    void reduce_lattice(Matrix& L, Vector& D, Matrix& Z) {
        for (size_t i = 0; i < N; ++i) {
            for (size_t j = 0; j < N; ++j) {
                Z[i][j] = (i == j) ? 1.0 : 0.0;
            }
        }

        int i = static_cast<int>(N) - 2;
        while (i >= 0) {
            gauss_transform(L, Z, i + 1, i);

            double delta = D[i] + L[i + 1][i] * L[i + 1][i] * D[i + 1];
            if (delta + 1e-9 < D[i + 1]) {
                swap_coordinates(L, D, Z, static_cast<size_t>(i));
                for (size_t k = i + 1; k < N; ++k) {
                    for (int m = i; m >= 0; --m) {
                        gauss_transform(L, Z, k, static_cast<size_t>(m));
                    }
                }
                i = static_cast<int>(N) - 2;
            } else {
                --i;
            }
        }
    }

    void search_tree(const Matrix& L, const Vector& D, const Vector& z_hat,
                     Vector& z_fix1, Vector& z_fix2, double& f1, double& f2) {
        int i = static_cast<int>(N) - 1;
        double max_dist = 1e9;
        f1 = max_dist;
        f2 = max_dist;

        Vector z{}, step{}, dist{}, z_cond{};
        z_cond[i] = z_hat[i];
        z[i] = std::round(z_cond[i]);
        step[i] = (z_cond[i] >= z[i]) ? 1.0 : -1.0;

        int candidates = 0;

        while (true) {
            double diff = z[i] - z_cond[i];
            double new_dist = dist[i] + diff * diff * D[i];

            if (new_dist < max_dist) {
                if (i > 0) {
                    --i;
                    dist[i] = new_dist;
                    double cond = z_hat[i];
                    for (size_t j = i + 1; j < N; ++j) {
                        cond -= L[j][i] * (z[j] - z_hat[j]);
                    }
                    z_cond[i] = cond;
                    z[i] = std::round(z_cond[i]);
                    step[i] = (z_cond[i] >= z[i]) ? 1.0 : -1.0;
                } else {
                    if (new_dist < f1) {
                        f2 = f1;
                        z_fix2 = z_fix1;
                        f1 = new_dist;
                        z_fix1 = z;
                    } else if (new_dist < f2) {
                        f2 = new_dist;
                        z_fix2 = z;
                    }
                    if (++candidates >= 2) {
                        max_dist = f2;
                    }
                    z[i] += step[i];
                    step[i] = -step[i] - ((step[i] > 0) ? 1.0 : -1.0);
                }
            } else {
                if (i == static_cast<int>(N) - 1) break;
                ++i;
                z[i] += step[i];
                step[i] = -step[i] - ((step[i] > 0) ? 1.0 : -1.0);
            }
        }
    }
};

} // namespace rtk

int main() {
    constexpr size_t N = 3;
    rtk::LambdaSolver<N>::Vector a_hat = { 5.45, 12.35, 8.85 };
    rtk::LambdaSolver<N>::Matrix Q_a = {{
        { 6.25, 6.15, 6.05 },
        { 6.15, 6.30, 6.10 },
        { 6.05, 6.10, 6.20 }
    }};

    rtk::LambdaSolver<N> solver;
    auto res = solver.solve(a_hat, Q_a, 2.5);

    std::cout << std::fixed << std::setprecision(2);
    std::cout << "Float оцінки:   [ " << a_hat[0] << ", " << a_hat[1] << ", " << a_hat[2] << " ]\n";
    std::cout << "Fixed вектор 1: [ " << res.fix1[0] << ", " << res.fix1[1] << ", " << res.fix1[2]
              << " ]  (F1 = " << std::setprecision(5) << res.f1 << ")\n";
    std::cout << "Fixed вектор 2: [ " << res.fix2[0] << ", " << res.fix2[1] << ", " << res.fix2[2]
              << " ]  (F2 = " << res.f2 << ")\n";
    std::cout << "Ratio-Test:     " << std::setprecision(2) << res.ratio << " -> "
              << (res.is_fixed ? "FIXED" : "FLOAT") << "\n";

    return 0;
}
