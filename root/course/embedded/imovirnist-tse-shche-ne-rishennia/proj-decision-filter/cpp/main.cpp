#include <cstdint>
#include <cmath>
#include <algorithm>
#include <chrono>
#include <bit>

class DecisionConfidenceFilter {
public:
    struct Config {
        float alpha{0.75f};              // Коефіцієнт згладжування інтегратора EMA
        float thresh_on{0.75f};          // Поріг активації (H_on)
        float thresh_off{0.35f};         // Поріг деактивації (H_off)
        uint32_t min_hold_ms{300};       // Мінімальний час утримання активного стану (мс)
        uint8_t window_size{10};         // Розмір вікна голосування (кадри, N <= 32)
        uint8_t min_votes{6};            // Необхідна кількість підтверджень (M)
    };

    explicit constexpr DecisionConfidenceFilter(const Config& config = Config{}) noexcept
        : cfg_(config), integrated_score_(0.0f), history_mask_(0U),
          state_entered_ms_(0U), is_active_(false) {}

    // Температурне калібрування сирих логітів
    [[nodiscard]] static float calibrateTemperature(float logit_target, float logit_bg, float temperature) noexcept {
        const float temp = (temperature > 0.001f) ? temperature : 1.0f;
        const float st = logit_target / temp;
        const float sbg = logit_bg / temp;
        const float max_l = std::max(st, sbg);
        const float exp_t = std::exp(st - max_l);
        const float exp_bg = std::exp(sbg - max_l);
        return exp_t / (exp_t + exp_bg);
    }

    // Оновлення стану фільтра за новим виміром
    bool update(float raw_prob, uint32_t now_ms) noexcept {
        // 1. Інтегрування експоненційним середнім
        integrated_score_ = (cfg_.alpha * integrated_score_) + ((1.0f - cfg_.alpha) * raw_prob);

        // 2. Бітове голосування M-з-N
        const bool frame_hit = (raw_prob >= cfg_.thresh_off);
        history_mask_ = (history_mask_ << 1U) | (frame_hit ? 1U : 0U);

        const uint32_t valid_mask = (cfg_.window_size >= 32) ? 0xFFFFFFFFU : ((1U << cfg_.window_size) - 1U);
        const uint32_t current_window = history_mask_ & valid_mask;
        const int votes = std::popcount(current_window);
        const bool vote_passed = (votes >= static_cast<int>(cfg_.min_votes));

        // 3. Логіка гістерезису та часового утримання
        if (is_active_) {
            const bool hold_expired = (now_ms - state_entered_ms_) >= cfg_.min_hold_ms;
            if (hold_expired && (integrated_score_ < cfg_.thresh_off) && !vote_passed) {
                is_active_ = false;
                state_entered_ms_ = now_ms;
            }
        } else {
            if ((integrated_score_ >= cfg_.thresh_on) || vote_passed) {
                is_active_ = true;
                state_entered_ms_ = now_ms;
            }
        }

        return is_active_;
    }

    [[nodiscard]] float integratedScore() const noexcept { return integrated_score_; }
    [[nodiscard]] bool isActive() const noexcept { return is_active_; }

    void reset() noexcept {
        integrated_score_ = 0.0f;
        history_mask_ = 0U;
        state_entered_ms_ = 0U;
        is_active_ = false;
    }

private:
    Config cfg_;
    float integrated_score_{0.0f};
    uint32_t history_mask_{0U};
    uint32_t state_entered_ms_{0U};
    bool is_active_{false};
};
