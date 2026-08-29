#pragma once

// Фільтр впевненості: калібрування -> інтегратор витоку -> голосування M-з-N
// -> автомат із гістерезисом і таймером утримання.
// Клас — заголовковий і тривіально копійовний: жодного динамічного стану,
// тож масив таких фільтрів лягає у статичну пам'ять як є.

#include <algorithm>
#include <bit>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <expected>
#include <string_view>

using Millis = std::chrono::milliseconds;

enum class ConfigError {
    Temperature,   // T мусить бути додатною скінченною
    Alpha,         // alpha поза (0, 1)
    Thresholds,    // пороги поза [0, 1] або H_off вище за H_on
    WindowSize,    // вікно поза 1..32 кадрів
    VoteCount,     // M поза 1..N
};

[[nodiscard]] constexpr std::string_view describe(ConfigError error) noexcept {
    switch (error) {
        case ConfigError::Temperature: return "температура мусить бути додатною";
        case ConfigError::Alpha:       return "alpha мусить лежати в (0, 1)";
        case ConfigError::Thresholds:  return "пороги зіпсовані: H_off вище за H_on";
        case ConfigError::WindowSize:  return "вікно голосування поза 1..32 кадрів";
        case ConfigError::VoteCount:   return "M мусить лежати в 1..N";
    }
    return "невідома вада конфігурації";
}

class DecisionConfidenceFilter {
public:
    // Глибша історія не влізе: вікно живе в одному 32-бітному слові.
    static constexpr std::uint8_t kMaxWindow = 32;

    struct Config {
        float temperature{2.0f};      // T для калібрування логітів
        float alpha{0.75f};           // коефіцієнт витоку EMA
        float thresh_on{0.70f};       // H_on — поріг активації
        float thresh_off{0.35f};      // H_off — деактивація і поріг біта голосування
        Millis min_hold{200};         // t_hold — мінімальна тривалість тривоги
        std::uint8_t window_size{5};  // N — глибина вікна
        std::uint8_t min_votes{3};    // M — потрібних підтверджень
        bool fail_safe_start{false};  // холодний старт одразу в тривозі
    };

    // Перевіряємо пороги один раз на створенні; у гарячому шляху перевірок нема.
    [[nodiscard]] static std::expected<void, ConfigError> validate(const Config& cfg) noexcept {
        if (!(cfg.temperature > 0.0f) || !std::isfinite(cfg.temperature)) {
            return std::unexpected(ConfigError::Temperature);
        }
        if (!(cfg.alpha > 0.0f) || !(cfg.alpha < 1.0f)) {
            return std::unexpected(ConfigError::Alpha);
        }
        // Зворотний гістерезис перетворив би автомат на генератор брязкоту —
        // саме на те, від чого фільтр і рятує.
        if (cfg.thresh_off < 0.0f || cfg.thresh_on > 1.0f || cfg.thresh_off > cfg.thresh_on) {
            return std::unexpected(ConfigError::Thresholds);
        }
        if (cfg.window_size == 0 || cfg.window_size > kMaxWindow) {
            return std::unexpected(ConfigError::WindowSize);
        }
        if (cfg.min_votes == 0 || cfg.min_votes > cfg.window_size) {
            return std::unexpected(ConfigError::VoteCount);
        }
        return {};
    }

    [[nodiscard]] static std::expected<DecisionConfidenceFilter, ConfigError>
    make(const Config& cfg, Millis now = Millis{0}) noexcept {
        if (auto ok = validate(cfg); !ok) {
            return std::unexpected(ok.error());
        }
        return DecisionConfidenceFilter{cfg, now};
    }

    // Конфігурація вважається вже перевіреною: пул створює десятки фільтрів
    // з однієї перевіреної Config і не повторює перевірку на кожен слот.
    explicit constexpr DecisionConfidenceFilter(const Config& cfg = Config{},
                                                Millis now = Millis{0}) noexcept
        : cfg_{cfg},
          state_entered_{now},
          last_update_{now},
          is_active_{cfg.fail_safe_start} {}

    // Температурне калібрування пари логітів «об'єкт проти фону».
    // Віднімання максимуму тримає аргумент std::exp у межах (-inf, 0],
    // тож переповнення до +inf неможливе за побудовою.
    [[nodiscard]] static float calibrate(float logit_target, float logit_bg,
                                         float temperature) noexcept {
        const float temp = (temperature > 0.0f && std::isfinite(temperature)) ? temperature : 1.0f;
        const float scaled_target = logit_target / temp;
        const float scaled_bg = logit_bg / temp;

        const float max_l = std::max(scaled_target, scaled_bg);
        const float exp_target = std::exp(scaled_target - max_l);
        const float exp_bg = std::exp(scaled_bg - max_l);

        const float sum = exp_target + exp_bg;
        return (sum > 0.0f) ? exp_target / sum : 0.0f;
    }

    // Один такт конвеєра. Повертає стабільний вихід після цього такту.
    bool update(float raw_prob, Millis now) noexcept {
        // Затискання через заперечення ловить і NaN: одне NaN з детектора
        // отруїло б інтегратор назавжди, бо NaN * alpha = NaN.
        float p = (raw_prob >= 0.0f) ? std::min(raw_prob, 1.0f) : 0.0f;

        // 1. Інтегратор витоку: S[k] = alpha * S[k-1] + (1 - alpha) * P[k].
        integrated_score_ = cfg_.alpha * integrated_score_ + (1.0f - cfg_.alpha) * p;

        // 2. Кадр квантується в один біт і в'їжджає в історію зсувом.
        history_ = (history_ << 1U) | (p >= cfg_.thresh_off ? 1U : 0U);
        const bool vote_passed = votes() >= cfg_.min_votes;

        // 3. Автомат із подвійним гістерезисом і таймером утримання.
        if (is_active_) {
            const bool hold_expired = (now - state_entered_) >= cfg_.min_hold;
            if (hold_expired && integrated_score_ < cfg_.thresh_off && !vote_passed) {
                is_active_ = false;
                state_entered_ = now;
            }
        } else if (integrated_score_ >= cfg_.thresh_on || vote_passed) {
            is_active_ = true;
            state_entered_ = now;
        }

        last_update_ = now;
        return is_active_;
    }

    // Той самий такт, але від сирих логітів мережі.
    bool updateLogits(float logit_target, float logit_bg, Millis now) noexcept {
        return update(calibrate(logit_target, logit_bg, cfg_.temperature), now);
    }

    // Вікно, обрізане до window_size бітів. Зсув 1U << 32 — невизначена
    // поведінка, тому повна ширина обробляється окремою гілкою.
    [[nodiscard]] constexpr std::uint32_t window() const noexcept {
        const std::uint32_t mask = (cfg_.window_size >= kMaxWindow)
                                       ? 0xFFFF'FFFFU
                                       : ((1U << cfg_.window_size) - 1U);
        return history_ & mask;
    }

    // popcount — одна інструкція ALU, без циклу: цикл у перериванні дав би
    // розкид часу виконання.
    [[nodiscard]] constexpr int votes() const noexcept {
        return std::popcount(window());
    }

    [[nodiscard]] constexpr float score() const noexcept { return integrated_score_; }
    [[nodiscard]] constexpr bool isActive() const noexcept { return is_active_; }
    [[nodiscard]] constexpr const Config& config() const noexcept { return cfg_; }

    [[nodiscard]] constexpr Millis idleFor(Millis now) const noexcept {
        return now - last_update_;
    }

    void reset(Millis now = Millis{0}) noexcept {
        integrated_score_ = 0.0f;
        history_ = 0U;
        state_entered_ = now;
        last_update_ = now;
        is_active_ = cfg_.fail_safe_start;
    }

private:
    Config cfg_{};
    float integrated_score_{0.0f};
    std::uint32_t history_{0U};
    Millis state_entered_{0};
    Millis last_update_{0};
    bool is_active_{false};
};
