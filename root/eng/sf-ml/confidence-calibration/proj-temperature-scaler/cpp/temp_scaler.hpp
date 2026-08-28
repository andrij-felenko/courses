// ============================================================================
// Файл: temp_scaler.hpp
// Опис: Інженерний модуль калібрування впевненості логітів нейромережі (C++20)
// ============================================================================
#ifndef TEMP_SCALER_HPP
#define TEMP_SCALER_HPP

#include <span>
#include <vector>
#include <array>
#include <cmath>
#include <algorithm>
#include <numeric>
#include <expected>
#include <limits>
#include <cstddef>

namespace ml_safety {

enum class Status {
    Success = 0,
    InvalidParameter,
    BufferOverflow,
    NumericalInstability,
    OptimizationFailed
};

struct Decision {
    std::size_t predicted_class{0};
    float calibrated_confidence{0.0f};
    bool is_safe_to_execute{false};
};

struct Metrics {
    float ece{0.0f};
    float mce{0.0f};
    float brier_score{0.0f};
    float nll{0.0f};
};

struct DatasetSample {
    std::span<const float> logits;
    std::size_t true_label;
};

class TemperatureScaler {
public:
    static constexpr std::size_t MaxStackClasses = 128;
    static constexpr std::size_t MaxBins = 64;

    /**
     * @brief Чисельно стабільне калібрування логітів із поверненням ймовірностей у векторі
     */
    static std::expected<std::vector<float>, Status> 
    calibrate(std::span<const float> logits, float temperature) noexcept {
        if (logits.empty() || temperature <= 0.0f || std::isnan(temperature)) {
            return std::unexpected(Status::InvalidParameter);
        }

        std::vector<float> probs(logits.size());
        auto res = calibrate_to_span(logits, temperature, probs);
        if (!res) {
            return std::unexpected(res.error());
        }
        return probs;
    }

    /**
     * @brief Калібрування логітів у попередньо виділений буфер (Zero Heap Allocation)
     */
    static std::expected<void, Status> 
    calibrate_to_span(std::span<const float> logits, float temperature, 
                      std::span<float> out_probs) noexcept {
        if (logits.empty() || out_probs.size() < logits.size() || 
            temperature <= 0.0f || std::isnan(temperature)) {
            return std::unexpected(Status::InvalidParameter);
        }

        const float inv_t = 1.0f / temperature;

        // Крок 1: Пошук максимального масштабованого логіта для Log-Sum-Exp стабілізації
        float max_scaled = -std::numeric_limits<float>::infinity();
        for (float val : logits) {
            float scaled = val * inv_t;
            if (scaled > max_scaled) {
                max_scaled = scaled;
            }
        }

        if (std::isinf(max_scaled) || std::isnan(max_scaled)) {
            return std::unexpected(Status::NumericalInstability);
        }

        // Крок 2: Обчислення експонент та їх акумуляція
        float sum_exp = 0.0f;
        for (std::size_t i = 0; i < logits.size(); ++i) {
            float exp_val = std::exp(logits[i] * inv_t - max_scaled);
            out_probs[i] = exp_val;
            sum_exp += exp_val;
        }

        if (sum_exp <= 0.0f || std::isnan(sum_exp) || std::isinf(sum_exp)) {
            return std::unexpected(Status::NumericalInstability);
        }

        // Крок 3: Нормалізація
        const float inv_sum = 1.0f / sum_exp;
        for (std::size_t i = 0; i < logits.size(); ++i) {
            out_probs[i] *= inv_sum;
        }

        return {};
    }

    /**
     * @brief Прийняття порогового рішення з перевіркою безпеки
     */
    static std::expected<Decision, Status>
    evaluate_decision(std::span<const float> logits, float temperature, 
                      float safety_threshold) noexcept {
        if (logits.empty() || logits.size() > MaxStackClasses) {
            return std::unexpected(Status::InvalidParameter);
        }

        std::array<float, MaxStackClasses> stack_probs;
        std::span<float> probs_span(stack_probs.data(), logits.size());

        auto cal_res = calibrate_to_span(logits, temperature, probs_span);
        if (!cal_res) {
            return std::unexpected(cal_res.error());
        }

        std::size_t best_idx = 0;
        float max_conf = probs_span[0];
        for (std::size_t i = 1; i < logits.size(); ++i) {
            if (probs_span[i] > max_conf) {
                max_conf = probs_span[i];
                best_idx = i;
            }
        }

        return Decision{
            .predicted_class = best_idx,
            .calibrated_confidence = max_conf,
            .is_safe_to_execute = (max_conf >= safety_threshold)
        };
    }

    /**
     * @brief Розрахунок метрик калібрування на наборі зразків
     */
    static std::expected<Metrics, Status>
    compute_metrics(std::span<const DatasetSample> dataset, float temperature, 
                    std::size_t num_bins = 15) noexcept {
        if (dataset.empty() || num_bins == 0 || num_bins > MaxBins || temperature <= 0.0f) {
            return std::unexpected(Status::InvalidParameter);
        }

        struct BinAccumulator {
            std::size_t count{0};
            double confidence_sum{0.0};
            std::size_t correct_count{0};
        };

        std::array<BinAccumulator, MaxBins> bins{};
        const float bin_width = 1.0f / static_cast<float>(num_bins);

        double total_nll = 0.0;
        double total_brier = 0.0;
        std::array<float, MaxStackClasses> prob_buf;

        for (const auto& sample : dataset) {
            if (sample.logits.size() > MaxStackClasses) {
                return std::unexpected(Status::BufferOverflow);
            }
            std::span<float> probs(prob_buf.data(), sample.logits.size());
            auto cal_res = calibrate_to_span(sample.logits, temperature, probs);
            if (!cal_res) return std::unexpected(cal_res.error());

            // Пошук передбаченого класу та впевненості
            std::size_t pred_class = 0;
            float max_prob = probs[0];
            for (std::size_t c = 1; c < probs.size(); ++c) {
                if (probs[c] > max_prob) {
                    max_prob = probs[c];
                    pred_class = c;
                }
            }

            bool is_correct = (pred_class == sample.true_label);
            float conf = std::clamp(max_prob, 0.0f, 1.0f);

            std::size_t bin_idx = std::min(static_cast<std::size_t>(conf / bin_width), num_bins - 1);
            bins[bin_idx].count++;
            bins[bin_idx].confidence_sum += conf;
            if (is_correct) {
                bins[bin_idx].correct_count++;
            }

            // NLL
            if (sample.true_label < probs.size()) {
                float p_true = std::max(probs[sample.true_label], 1e-12f);
                total_nll -= std::log(static_cast<double>(p_true));
            }

            // Brier
            for (std::size_t c = 0; c < probs.size(); ++c) {
                double target = (c == sample.true_label) ? 1.0 : 0.0;
                double diff = static_cast<double>(probs[c]) - target;
                total_brier += diff * diff;
            }
        }

        const double n_samples = static_cast<double>(dataset.size());
        double total_ece = 0.0;
        double max_mce = 0.0;

        for (std::size_t b = 0; b < num_bins; ++b) {
            if (bins[b].count > 0) {
                double avg_conf = bins[b].confidence_sum / static_cast<double>(bins[b].count);
                double avg_acc = static_cast<double>(bins[b].correct_count) / static_cast<double>(bins[b].count);
                double gap = std::abs(avg_acc - avg_conf);
                double weight = static_cast<double>(bins[b].count) / n_samples;
                total_ece += weight * gap;
                if (gap > max_mce) {
                    max_mce = gap;
                }
            }
        }

        return Metrics{
            .ece = static_cast<float>(total_ece),
            .mce = static_cast<float>(max_mce),
            .brier_score = static_cast<float>(total_brier / n_samples),
            .nll = static_cast<float>(total_nll / n_samples)
        };
    }

    /**
     * @brief Оптимізація скалярної температури методом золотого перетину
     */
    static std::expected<float, Status>
    optimize_temperature(std::span<const DatasetSample> dataset,
                         float min_temp = 0.1f, float max_temp = 10.0f,
                         std::size_t max_iterations = 35, float tolerance = 1e-5f) noexcept {
        if (dataset.empty() || min_temp <= 0.0f || max_temp <= min_temp) {
            return std::unexpected(Status::InvalidParameter);
        }

        // Оптимізуємо за оберненою температурою beta = 1 / T
        double beta_min = 1.0 / static_cast<double>(max_temp);
        double beta_max = 1.0 / static_cast<double>(min_temp);

        auto evaluate_nll_beta = [&](double beta) -> double {
            double sum_nll = 0.0;
            std::array<float, MaxStackClasses> exp_buf;

            for (const auto& sample : dataset) {
                if (sample.logits.size() > MaxStackClasses) return 1e9;

                // Log-Sum-Exp
                double max_scaled = -std::numeric_limits<double>::infinity();
                for (float z : sample.logits) {
                    double val = static_cast<double>(z) * beta;
                    if (val > max_scaled) max_scaled = val;
                }

                double sum_exp = 0.0;
                for (std::size_t i = 0; i < sample.logits.size(); ++i) {
                    double e = std::exp(static_cast<double>(sample.logits[i]) * beta - max_scaled);
                    exp_buf[i] = static_cast<float>(e);
                    sum_exp += e;
                }

                if (sample.true_label < sample.logits.size()) {
                    double log_p_true = (static_cast<double>(sample.logits[sample.true_label]) * beta - max_scaled) - std::log(sum_exp);
                    sum_nll -= log_p_true;
                }
            }
            return sum_nll / static_cast<double>(dataset.size());
        };

        const double phi_res = 0.38196601125010515; // 2 - (sqrt(5) + 1)/2

        double a = beta_min;
        double b = beta_max;
        double c = a + phi_res * (b - a);
        double d = b - phi_res * (b - a);
        double fc = evaluate_nll_beta(c);
        double fd = evaluate_nll_beta(d);

        for (std::size_t iter = 0; iter < max_iterations; ++iter) {
            if (std::abs(b - a) < static_cast<double>(tolerance)) {
                break;
            }

            if (fc < fd) {
                b = d;
                d = c;
                fd = fc;
                c = a + phi_res * (b - a);
                fc = evaluate_nll_beta(c);
            } else {
                a = c;
                c = d;
                fc = fd;
                d = b - phi_res * (b - a);
                fd = evaluate_nll_beta(d);
            }
        }

        double best_beta = (a + b) * 0.5;
        if (best_beta <= 0.0) {
            return std::unexpected(Status::OptimizationFailed);
        }

        return static_cast<float>(1.0 / best_beta);
    }
};

} // namespace ml_safety

#endif // TEMP_SCALER_HPP
