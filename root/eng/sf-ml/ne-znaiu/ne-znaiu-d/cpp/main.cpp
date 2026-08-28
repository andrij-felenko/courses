#include <iostream>
#include <cmath>
#include <array>
#include <span>
#include <expected>
#include <algorithm>
#include <numeric>

enum class DecisionStatus {
    Accepted,
    RejectOOD,
    RejectAmbiguous
};

struct SelectiveResult {
    int class_id{-1};
    float confidence{0.0f};
    float energy{0.0f};
    float normalized_entropy{0.0f};
    DecisionStatus status{DecisionStatus::Accepted};
};

template <std::size_t MaxClasses = 8>
class SelectiveClassifier {
public:
    struct Config {
        float temperature{1.0f};
        float energy_threshold{-5.0f};
        float entropy_threshold{0.45f};
    };

    explicit constexpr SelectiveClassifier(Config cfg) noexcept : cfg_(cfg) {}

    [[nodiscard]] std::expected<SelectiveResult, const char*> evaluate(
        std::span<const float> logits
    ) const noexcept {
        if (logits.empty() || logits.size() > MaxClasses || cfg_.temperature <= 0.0f) {
            return std::unexpected("Некоректний розмір вектора логітів або температура");
        }

        SelectiveResult res{};
        const auto num_classes = logits.size();

        // 1. Пошук максимального логіта (запобігання переповненню expf)
        const auto max_it = std::max_element(logits.begin(), logits.end());
        const float max_logit = *max_it;
        res.class_id = static_cast<int>(std::distance(logits.begin(), max_it));

        // 2. Обчислення вільної енергії Гельмгольца
        std::array<float, MaxClasses> exp_scaled{};
        float sum_exp = 0.0f;
        for (std::size_t i = 0; i < num_classes; ++i) {
            exp_scaled[i] = std::exp((logits[i] - max_logit) / cfg_.temperature);
            sum_exp += exp_scaled[i];
        }

        res.energy = -cfg_.temperature * ((max_logit / cfg_.temperature) + std::log(sum_exp));

        if (res.energy > cfg_.energy_threshold) {
            res.status = DecisionStatus::RejectOOD;
            return res;
        }

        // 3. Розрахунок нормованої ентропії Шеннона
        float entropy = 0.0f;
        for (std::size_t i = 0; i < num_classes; ++i) {
            const float p = exp_scaled[i] / sum_exp;
            if (p > 1e-8f) {
                entropy -= p * std::log(p);
            }
        }

        const float max_entropy = std::log(static_cast<float>(num_classes));
        res.normalized_entropy = (max_entropy > 0.0f) ? (entropy / max_entropy) : 0.0f;
        res.confidence = exp_scaled[static_cast<std::size_t>(res.class_id)] / sum_exp;

        if (res.normalized_entropy > cfg_.entropy_threshold) {
            res.status = DecisionStatus::RejectAmbiguous;
            return res;
        }

        res.status = DecisionStatus::Accepted;
        return res;
    }

private:
    Config cfg_;
};
