#include <vector>
#include <span>
#include <cmath>
#include <numeric>
#include <expected>
#include <random>
#include <algorithm>

enum class CovError {
    InvalidDimensions,
    NotEnoughSamples,
    NotPositiveDefinite
};

struct MultivariateStats {
    std::vector<double> mean;
    std::vector<double> covariance; // матриця D x D у форматі row-major
    size_t dim{0};
};

/* Обчислення середнього та вибіркової коваріації для набору D-вимірних векторів */
[[nodiscard]] std::expected<MultivariateStats, CovError> compute_sample_covariance(
    std::span<const double> flat_samples,
    size_t num_samples,
    size_t dim
) {
    if (dim == 0 || flat_samples.size() != num_samples * dim) {
        return std::unexpected(CovError::InvalidDimensions);
    }
    if (num_samples < 2) {
        return std::unexpected(CovError::NotEnoughSamples);
    }

    MultivariateStats result{
        .mean = std::vector<double>(dim, 0.0),
        .covariance = std::vector<double>(dim * dim, 0.0),
        .dim = dim
    };

    // 1. Вибіркове середнє
    for (size_t j = 0; j < dim; ++j) {
        double acc = 0.0;
        for (size_t k = 0; k < num_samples; ++k) {
            acc += flat_samples[k * dim + j];
        }
        result.mean[j] = acc / static_cast<double>(num_samples);
    }

    // 2. Незсунена коваріаційна матриця з поправкою Бесселя (N - 1)
    const double inv_df = 1.0 / static_cast<double>(num_samples - 1);
    for (size_t i = 0; i < dim; ++i) {
        for (size_t j = 0; j <= i; ++j) {
            double acc = 0.0;
            for (size_t k = 0; k < num_samples; ++k) {
                double diff_i = flat_samples[k * dim + i] - result.mean[i];
                double diff_j = flat_samples[k * dim + j] - result.mean[j];
                acc += diff_i * diff_j;
            }
            double cov_val = acc * inv_df;
            result.covariance[i * dim + j] = cov_val;
            result.covariance[j * dim + i] = cov_val;
        }
    }

    return result;
}

/* Розклад Холецького: знаходження нижньотрикутної матриці L такої, що S = L * L^T */
[[nodiscard]] std::expected<std::vector<double>, CovError> cholesky_decompose(
    std::span<const double> cov_matrix,
    size_t dim,
    double epsilon = 1e-12
) {
    if (cov_matrix.size() != dim * dim || dim == 0) {
        return std::unexpected(CovError::InvalidDimensions);
    }

    std::vector<double> l_matrix(dim * dim, 0.0);

    for (size_t j = 0; j < dim; ++j) {
        double sum_sq = 0.0;
        for (size_t k = 0; k < j; ++k) {
            double val = l_matrix[j * dim + k];
            sum_sq += val * val;
        }

        double diag_val = cov_matrix[j * dim + j] - sum_sq;
        if (diag_val <= epsilon) {
            return std::unexpected(CovError::NotPositiveDefinite);
        }

        double l_jj = std::sqrt(diag_val);
        l_matrix[j * dim + j] = l_jj;
        double inv_l_jj = 1.0 / l_jj;

        for (size_t i = j + 1; i < dim; ++i) {
            double sum_prod = 0.0;
            for (size_t k = 0; k < j; ++k) {
                sum_prod += l_matrix[i * dim + k] * l_matrix[j * dim + k];
            }
            l_matrix[i * dim + j] = (cov_matrix[i * dim + j] - sum_prod) * inv_l_jj;
        }
    }

    return l_matrix;
}

/* Генератор випадкових корельованих векторів */
class CorrelatedGaussianSampler {
public:
    CorrelatedGaussianSampler(
        std::vector<double> mean,
        std::vector<double> cholesky_l,
        size_t dim,
        uint64_t seed = 42
    ) : mean_(std::move(mean)), l_matrix_(std::move(cholesky_l)), dim_(dim), rng_(seed), dist_(0.0, 1.0) {}

    std::vector<double> sample() {
        std::vector<double> z(dim_);
        for (double &val : z) {
            val = dist_(rng_);
        }

        std::vector<double> y = mean_;
        for (size_t i = 0; i < dim_; ++i) {
            for (size_t k = 0; k <= i; ++k) {
                y[i] += l_matrix_[i * dim_ + k] * z[k];
            }
        }
        return y;
    }

private:
    std::vector<double> mean_;
    std::vector<double> l_matrix_;
    size_t dim_;
    std::mt19937_64 rng_;
    std::normal_distribution<double> dist_;
};
