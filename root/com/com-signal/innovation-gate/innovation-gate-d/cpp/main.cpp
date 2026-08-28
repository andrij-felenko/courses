#include <array>
#include <cmath>
#include <cstdint>
#include <span>
#include <expected>

enum class GatingDecision : uint8_t {
    Accepted = 0,     // Вимір повністю відповідає гаусовій моделі
    SoftScaled,      // Вимір у зоні сумніву: коваріацію шуму масштабовано
    RejectedOutlier, // Одиничний грубий викид: вимір пропущено
    DivergenceAlarm  // Систематична розбіжність фільтра: потрібен ресет
};

struct GatingResult {
    GatingDecision decision;
    float mahalanobis_sq; // d²
    float noise_scaling;  // Множник для матриці R
};

template <size_t WindowSize = 32>
class InnovationGate2D {
public:
    constexpr InnovationGate2D(float gamma_1 = 5.99f, float gamma_2 = 11.83f, uint8_t max_rejects = 10) noexcept
        : gamma_1_(gamma_1), gamma_2_(gamma_2), max_allowed_rejects_(max_rejects) {
        nis_history_.fill(0.0f);
    }

    [[nodiscard]] GatingResult validate(
        std::span<const float, 2> y,
        const std::array<std::array<float, 2>, 2>& S
    ) noexcept {
        // 1. Детермінант матриці S розміру 2x2
        const float det = S[0][0] * S[1][1] - S[0][1] * S[1][0];

        if (det <= 1e-12f) [[unlikely]] {
            ++consecutive_rejects_;
            return {
                .decision = (consecutive_rejects_ >= max_allowed_rejects_) 
                            ? GatingDecision::DivergenceAlarm 
                            : GatingDecision::RejectedOutlier,
                .mahalanobis_sq = 1e6f,
                .noise_scaling = 1.0f
            };
        }

        // 2. Аналітичне обернення S
        const float inv_det = 1.0f / det;
        const std::array<std::array<float, 2>, 2> S_inv{{
            {  S[1][1] * inv_det, -S[0][1] * inv_det },
            { -S[1][0] * inv_det,  S[0][0] * inv_det }
        }};

        // 3. Квадрат відстані Махаланобіса d² = yᵀ · S⁻¹ · y
        const float temp0 = S_inv[0][0] * y[0] + S_inv[0][1] * y[1];
        const float temp1 = S_inv[1][0] * y[0] + S_inv[1][1] * y[1];
        const float d2 = y[0] * temp0 + y[1] * temp1;

        // 4. Оновлення ковзного вікна NIS
        update_window(d2);

        // 5. Статистичне розгалуження
        if (d2 <= gamma_1_) {
            consecutive_rejects_ = 0;
            return {
                .decision = GatingDecision::Accepted,
                .mahalanobis_sq = d2,
                .noise_scaling = 1.0f
            };
        }

        if (d2 <= gamma_2_) {
            consecutive_rejects_ = 0;
            return {
                .decision = GatingDecision::SoftScaled,
                .mahalanobis_sq = d2,
                .noise_scaling = d2 / gamma_1_ // Huber-зважування
            };
        }

        // Зона відсікання
        ++consecutive_rejects_;
        
        if (consecutive_rejects_ >= max_allowed_rejects_ || is_statistically_diverged()) {
            return {
                .decision = GatingDecision::DivergenceAlarm,
                .mahalanobis_sq = d2,
                .noise_scaling = 1.0f
            };
        }

        return {
            .decision = GatingDecision::RejectedOutlier,
            .mahalanobis_sq = d2,
            .noise_scaling = 1.0f
        };
    }

    void reset() noexcept {
        consecutive_rejects_ = 0;
        history_idx_ = 0;
        history_count_ = 0;
        nis_window_sum_ = 0.0f;
        nis_history_.fill(0.0f);
    }

private:
    void update_window(float d2) noexcept {
        const float bounded_d2 = std::min(d2, gamma_2_ * 2.0f);
        nis_window_sum_ -= nis_history_[history_idx_];
        nis_history_[history_idx_] = bounded_d2;
        nis_window_sum_ += bounded_d2;

        history_idx_ = (history_idx_ + 1) % WindowSize;
        if (history_count_ < WindowSize) {
            ++history_count_;
        }
    }

    [[nodiscard]] bool is_statistically_diverged() const noexcept {
        if (history_count_ < WindowSize) {
            return false;
        }
        // Для 2D вимірів очікуване середнє E[d²] = 2.0
        const float mean_nis = nis_window_sum_ / static_cast<float>(WindowSize * 2);
        return mean_nis > 2.5f; // Суттєве перевищення довірчого інтервалу
    }

    float gamma_1_;
    float gamma_2_;
    uint8_t max_allowed_rejects_;
    uint8_t consecutive_rejects_{0};

    std::array<float, WindowSize> nis_history_{};
    size_t history_idx_{0};
    size_t history_count_{0};
    float nis_window_sum_{0.0f};
};
