#include <span>
#include <vector>
#include <cmath>
#include <algorithm>
#include <numeric>
#include <expected>
#include <cstddef>
#include <limits>

enum class CalibrationError {
    InvalidInput,
    ZeroTemperature,
    EmptyRange,
    CalculationOverflow
};

struct DecisionOutcome {
    std::size_t predicted_class;
    float calibrated_confidence;
    bool is_safe_to_execute;
};

class ConfidenceCalibrator {
public:
    /* Чисельно стабільний температурний Softmax у C++20 */
    static std::expected<std::vector<float>, CalibrationError> 
    scale_softmax(std::span<const float> logits, float temperature) noexcept {
        if (logits.empty()) {
            return std::unexpected(CalibrationError::EmptyRange);
        }
        if (temperature <= 0.0f || std::isnan(temperature)) {
            return std::unexpected(CalibrationError::ZeroTemperature);
        }

        const float inv_t = 1.0f / temperature;
        std::vector<float> probs(logits.size());

        // Знаходимо максимальний масштабований логіт для Log-Sum-Exp стабілізації
        float max_scaled = -std::numeric_limits<float>::infinity();
        for (float val : logits) {
            max_scaled = std::max(max_scaled, val * inv_t);
        }

        float sum_exp = 0.0f;
        for (std::size_t i = 0; i < logits.size(); ++i) {
            probs[i] = std::exp(logits[i] * inv_t - max_scaled);
            sum_exp += probs[i];
        }

        if (sum_exp <= 0.0f || std::isnan(sum_exp)) {
            return std::unexpected(CalibrationError::CalculationOverflow);
        }

        const float inv_sum = 1.0f / sum_exp;
        for (float& p : probs) {
            p *= inv_sum;
        }

        return probs;
    }

    /* Прийняття порогового рішення безпеки */
    static std::expected<DecisionOutcome, CalibrationError>
    evaluate_decision(std::span<const float> logits, float temperature, float safety_threshold) noexcept {
        auto probs_res = scale_softmax(logits, temperature);
        if (!probs_res) {
            return std::unexpected(probs_res.error());
        }

        const auto& probs = *probs_res;
        auto max_it = std::max_element(probs.begin(), probs.end());
        std::size_t best_class = static_cast<std::size_t>(std::distance(probs.begin(), max_it));
        float max_conf = *max_it;

        return DecisionOutcome{
            .predicted_class = best_class,
            .calibrated_confidence = max_conf,
            .is_safe_to_execute = (max_conf >= safety_threshold)
        };
    }

    /* Обчислення очікуваної похибки калібрування ECE */
    static float compute_ece(std::span<const float> confidences, 
                             std::span<const bool> correct_flags, 
                             std::size_t num_bins = 15) noexcept {
        if (confidences.empty() || confidences.size() != correct_flags.size() || num_bins == 0) {
            return 0.0f;
        }

        struct BinStat {
            std::size_t count = 0;
            double conf_sum = 0.0;
            size_t correct_count = 0;
        };

        std::vector<BinStat> bins(num_bins);
        const float bin_width = 1.0f / static_cast<float>(num_bins);

        for (std::size_t i = 0; i < confidences.size(); ++i) {
            float conf = std::clamp(confidences[i], 0.0f, 1.0f);
            size_t bin_idx = std::min(static_cast<size_t>(conf / bin_width), num_bins - 1);

            bins[bin_idx].count++;
            bins[bin_idx].conf_sum += conf;
            if (correct_flags[i]) {
                bins[bin_idx].correct_count++;
            }
        }

        double total_ece = 0.0;
        const double total_samples = static_cast<double>(confidences.size());

        for (const auto& bin : bins) {
            if (bin.count > 0) {
                double avg_conf = bin.conf_sum / static_cast<double>(bin.count);
                double avg_acc = static_cast<double>(bin.correct_count) / static_cast<double>(bin.count);
                double weight = static_cast<double>(bin.count) / total_samples;
                total_ece += weight * std::abs(avg_acc - avg_conf);
            }
        }

        return static_cast<float>(total_ece);
    }
};
