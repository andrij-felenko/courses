#include <iostream>
#include <string_view>
#include <expected>
#include <vector>
#include <cstdint>

// Ідіоматичний C++20: строгі типи, std::expected для обробки помилок, std::string_view

enum class DecisionRoute {
    FastTrackDelegate,
    TimeboxedSpike,
    PreMortemWorkshop,
    ArchReviewBoard,
    RejectedNoMetrics
};

struct DecisionVector {
    std::string_view title;
    float reversibility_score;       // 0.0 (важко відкотити) .. 1.0 (легко)
    std::uint8_t innovation_tokens;  // 0 .. 3
    bool has_measurement_data;       // чи є метрики
    std::uint8_t risk_severity;      // 1 .. 5
    bool touches_public_api;         // чи міняє публічний контракт
    bool is_performance_optimization; // чи це оптимізація продуктивності
};

struct EvaluationResult {
    DecisionRoute route;
    float one_way_index;
    std::string_view rationale;
};

enum class EvaluatorError {
    TokenBudgetExceeded,
    InvalidReversibilityScore,
    InvalidRiskSeverity
};

class DecisionEvaluator {
private:
    static constexpr std::uint8_t MAX_TOTAL_TOKENS = 3;
    std::uint8_t current_project_tokens_{1}; // Поточні жетони проєкту

public:
    explicit DecisionEvaluator(std::uint8_t current_tokens) 
        : current_project_tokens_(current_tokens) {}

    [[nodiscard]] std::expected<EvaluationResult, EvaluatorError> 
    evaluate(const DecisionVector& vec) const noexcept {
        if (vec.reversibility_score < 0.0f || vec.reversibility_score > 1.0f) {
            return std::unexpected(EvaluatorError::InvalidReversibilityScore);
        }
        if (vec.risk_severity < 1 || vec.risk_severity > 5) {
            return std::unexpected(EvaluatorError::InvalidRiskSeverity);
        }

        // Перевірка бюджету інноваційних жетонів (Boring Technology Heuristic)
        if (current_project_tokens_ + vec.innovation_tokens > MAX_TOTAL_TOKENS) {
            return std::unexpected(EvaluatorError::TokenBudgetExceeded);
        }

        // Евристика: Measure First
        if (vec.is_performance_optimization && !vec.has_measurement_data) {
            return EvaluationResult{
                .route = DecisionRoute::RejectedNoMetrics,
                .one_way_index = 0.0f,
                .rationale = "Відхилено: оптимізація продуктивності заборонена без метрик і профілювання"
            };
        }

        // Обчислення індексу односторонніх дверей (One-Way Door Index)
        const float public_impact = vec.touches_public_api ? 0.3f : 0.0f;
        const float token_impact = static_cast<float>(vec.innovation_tokens) * 0.1f;
        const float one_way_index = (1.0f - vec.reversibility_score) * 0.5f + public_impact + token_impact;

        // Покрокова фільтрація маршруту
        if (one_way_index >= 0.6f || vec.risk_severity >= 4) {
            return EvaluationResult{
                .route = DecisionRoute::ArchReviewBoard,
                .one_way_index = one_way_index,
                .rationale = "One-Way Door: Високий ризик або незворотність. Потрібен RFC та Arch Review Board."
            };
        }

        if (vec.risk_severity == 3 || (one_way_index >= 0.3f && !vec.has_measurement_data)) {
            return EvaluationResult{
                .route = DecisionRoute::PreMortemWorkshop,
                .one_way_index = one_way_index,
                .rationale = "Помірний ризик / невизначеність. Обов'язкова 30-хв сесія Pre-Mortem."
            };
        }

        if (vec.reversibility_score < 0.7f || vec.innovation_tokens > 0) {
            return EvaluationResult{
                .route = DecisionRoute::TimeboxedSpike,
                .one_way_index = one_way_index,
                .rationale = "Необхідно купити інформацію: Timeboxed спайк на 2 дні."
            };
        }

        return EvaluationResult{
            .route = DecisionRoute::FastTrackDelegate,
            .one_way_index = one_way_index,
            .rationale = "Two-Way Door: Висока зворотність. Делегувати розробнику негайно."
        };
    }
};

int main() {
    DecisionEvaluator evaluator(/*current_tokens=*/1);

    DecisionVector prop1{
        .title = "Додати новий кастомний брокер повідомлень",
        .reversibility_score = 0.2f,
        .innovation_tokens = 2,
        .has_measurement_data = false,
        .risk_severity = 4,
        .touches_public_api = true,
        .is_performance_optimization = false
    };

    auto res = evaluator.evaluate(prop1);
    if (res) {
        std::cout << "Рішення: " << res->rationale 
                  << " [One-Way Index: " << res->one_way_index << "]\n";
    } else {
        std::cout << "Помилка оцінки рішення (код " << static_cast<int>(res.error()) << ")\n";
    }

    return 0;
}
