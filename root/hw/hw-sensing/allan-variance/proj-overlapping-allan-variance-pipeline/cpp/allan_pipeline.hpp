#ifndef ALLAN_PIPELINE_HPP
#define ALLAN_PIPELINE_HPP

#include <vector>
#include <cmath>
#include <numeric>
#include <algorithm>
#include <execution>
#include <span>
#include <stdexcept>
#include <iostream>
#include <iomanip>

/**
 * @brief Структура збереження розрахованих значень тау, ADEV, MDEV, похибок та ступенів вільності.
 */
struct AllanResult {
    double tau{0.0};          ///< Час усереднення, с
    std::size_t m{0};         ///< Коефіцієнт кластеризації (кількість відліків у вікні)
    double adev{0.0};         ///< Перекривна девіація Аллана (OADEV)
    double mdev{0.0};         ///< Модифікована девіація Аллана (MDEV)
    double edf{0.0};          ///< Еквівалентні ступені вільності (EDF)
    double adev_lower{0.0};   ///< Нижня 95%-ва межа довірчого інтервалу
    double adev_upper{0.0};   ///< Верхня 95%-ва межа довірчого інтервалу
};

/**
 * @brief Шаблонний клас обчислення OAVAR, MVAR та довірчих інтервалів із підтримкою паралельної політики std::execution::par.
 * @tparam FloatType Тип чисел із рухомою комою (double або float)
 */
template <typename FloatType = double>
class AllanVariancePipeline {
public:
    /**
     * @brief Конструктор конвеєра з передачею періоду дискретизації.
     * @param dt Період дискретизації сенсора, с.
     */
    explicit AllanVariancePipeline(FloatType dt) : dt_(dt) {
        if (dt_ <= 0.0) {
            throw std::invalid_argument("Період дискретизації dt має бути строго додатним!");
        }
    }

    /**
     * @brief Завантаження та інтегрування вхідного часового ряду вимірювань у масив фази theta.
     * @param data Неперервний часовий зріз або контейнер відліків.
     */
    void set_data(std::span<const FloatType> data) {
        if (data.empty()) {
            throw std::invalid_argument("Вхідний масив даних не може бути порожнім!");
        }

        raw_size_ = data.size();
        theta_.resize(raw_size_ + 1);
        theta_[0] = 0.0;

        // Потокове накопичення інтеграла фази
        for (std::size_t i = 0; i < raw_size_; ++i) {
            theta_[i + 1] = theta_[i] + data[i] * dt_;
        }
    }

    /**
     * @brief Паралельний розрахунок девіацій Аллана для списку кроків кластеризації m.
     * @param m_grid Вектор цілочисельних масштабів кластеризації m.
     * @return Вектор результатів AllanResult для кожного тау.
     */
    [[nodiscard]] std::vector<AllanResult> compute_parallel(const std::vector<std::size_t>& m_grid) const {
        if (theta_.empty()) {
            throw std::logic_error("Дані сенсора не завантажено! Спочатку викличте set_data().");
        }

        std::vector<AllanResult> results(m_grid.size());

        // Паралельна обробка сітки tau між ядрами ЦП за допомогою std::execution::par
        std::vector<std::size_t> indices(m_grid.size());
        std::iota(indices.begin(), indices.end(), 0);

        std::for_each(std::execution::par, indices.begin(), indices.end(), [&](std::size_t idx) {
            const std::size_t m = m_grid[idx];
            AllanResult res;
            res.m = m;
            res.tau = static_cast<double>(m) * dt_;

            if (raw_size_ >= 2 * m + 1) {
                res.adev = compute_oadev_single(m);
                auto [edf, low, high] = compute_confidence(res.adev, m);
                res.edf = edf;
                res.adev_lower = low;
                res.adev_upper = high;
            }

            if (raw_size_ >= 3 * m) {
                res.mdev = compute_mdev_single(m);
            }

            results[idx] = res;
        });

        return results;
    }

private:
    FloatType dt_{0.0};
    std::size_t raw_size_{0};
    std::vector<FloatType> theta_{};

    [[nodiscard]] double compute_oadev_single(std::size_t m) const {
        const double tau = static_cast<double>(m) * dt_;
        const std::size_t limit = raw_size_ - 2 * m;
        double sum_sq = 0.0;

        for (std::size_t k = 0; k < limit; ++k) {
            const double diff = theta_[k + 2 * m] - 2.0 * theta_[k + m] + theta_[k];
            sum_sq += diff * diff;
        }

        const double oavar = sum_sq / (2.0 * tau * tau * static_cast<double>(limit));
        return std::sqrt(oavar);
    }

    [[nodiscard]] double compute_mdev_single(std::size_t m) const {
        const double tau = static_cast<double>(m) * dt_;
        const std::size_t num_terms = raw_size_ - 3 * m + 1;
        double sum_sq = 0.0;

        double running_sum = 0.0;
        for (std::size_t i = 0; i < m; ++i) {
            running_sum += (theta_[i + 2 * m] - 2.0 * theta_[i + m] + theta_[i]);
        }
        sum_sq += running_sum * running_sum;

        for (std::size_t j = 1; j < num_terms; ++j) {
            const double leaving = theta_[j - 1 + 2 * m] - 2.0 * theta_[j - 1 + m] + theta_[j - 1];
            const double entering = theta_[j + 3 * m - 1] - 2.0 * theta_[j + 2 * m - 1] + theta_[j + m - 1];
            running_sum += (entering - leaving);
            sum_sq += running_sum * running_sum;
        }

        const double norm = 2.0 * static_cast<double>(m * m) * tau * tau * static_cast<double>(num_terms);
        return std::sqrt(sum_sq / norm);
    }

    [[nodiscard]] std::tuple<double, double, double> compute_confidence(double adev, std::size_t m) const {
        const double n_f = static_cast<double>(raw_size_);
        const double m_f = static_cast<double>(m);
        double edf = (3.0 * (n_f - 1.0) / (2.0 * m_f) - (n_f - 2.0) / n_f) * (4.0 * m_f * m_f) / (4.0 * m_f * m_f + 5.0);
        if (edf < 1.0) edf = 1.0;

        const double z = 1.959964;
        const double factor = 2.0 / (9.0 * edf);
        const double term_low = 1.0 - factor - z * std::sqrt(factor);
        const double term_high = 1.0 - factor + z * std::sqrt(factor);

        const double chi2_low = edf * (term_low > 0.01 ? term_low * term_low * term_low : 0.0001);
        const double chi2_high = edf * (term_high * term_high * term_high);

        const double lower_bound = adev * std::sqrt(edf / chi2_high);
        const double upper_bound = adev * std::sqrt(edf / chi2_low);

        return {edf, lower_bound, upper_bound};
    }
};

#endif // ALLAN_PIPELINE_HPP
