#pragma once

#include <cstdint>
#include <array>
#include <algorithm>
#include <chrono>

enum class HysteresisMode : uint8_t {
    ActiveLow,  // Нагрівання: УВІМК при <= Low, ВИМК при >= High
    ActiveHigh  // Охолодження: УВІМК при >= High, ВИМК при <= Low
};

template <typename T = float, size_t MedianSize = 5>
class HysteresisController {
    static_assert(MedianSize >= 3 && MedianSize % 2 == 1, "MedianSize must be odd and >= 3");

public:
    struct Config {
        T threshold_low;
        T threshold_high;
        std::chrono::milliseconds min_on_time;
        std::chrono::milliseconds min_off_time;
        T ema_alpha{static_cast<T>(0.2)};
        HysteresisMode mode{HysteresisMode::ActiveLow};
    };

    explicit HysteresisController(const Config& config, std::chrono::milliseconds now = std::chrono::milliseconds{0})
        : config_(config), last_switch_time_(now) {}

    bool update(T raw_sample, std::chrono::milliseconds now) {
        // 1. Медіанний фільтр ковзного вікна
        median_buffer_[median_index_] = raw_sample;
        median_index_ = (median_index_ + 1) % MedianSize;
        if (median_count_ < MedianSize) {
            ++median_count_;
        }

        std::array<T, MedianSize> sort_buf{};
        std::copy_n(median_buffer_.begin(), median_count_, sort_buf.begin());
        std::sort(sort_buf.begin(), sort_buf.begin() + median_count_);
        const T median_val = sort_buf[median_count_ / 2];

        // 2. Експоненційний фільтр EMA
        if (!ema_initialized_) {
            ema_val_ = median_val;
            ema_initialized_ = true;
        } else {
            ema_val_ = config_.ema_alpha * median_val + (static_cast<T>(1) - config_.ema_alpha) * ema_val_;
        }

        // 3. Перевірка часового блокування (Hold-off)
        const auto elapsed = now - last_switch_time_;
        const auto required_hold = state_ ? config_.min_on_time : config_.min_off_time;

        if (elapsed < required_hold) {
            return state_; // Зміна стану заблокована таймером
        }

        // 4. Двопороговий тригер Шмітта
        bool desired_state = state_;
        if (config_.mode == HysteresisMode::ActiveLow) {
            if (ema_val_ <= config_.threshold_low) {
                desired_state = true;  // Охололо нижче порогу -> вмикаємо ТЕН
            } else if (ema_val_ >= config_.threshold_high) {
                desired_state = false; // Нагрілося до верхньої межі -> вимикаємо
            }
        } else {
            if (ema_val_ >= config_.threshold_high) {
                desired_state = true;  // Перегрів вище порогу -> вмикаємо компресор
            } else if (ema_val_ <= config_.threshold_low) {
                desired_state = false; // Охолоджено до норми -> вимикаємо
            }
        }

        if (desired_state != state_) {
            state_ = desired_state;
            last_switch_time_ = now;
        }

        return state_;
    }

    [[nodiscard]] bool state() const noexcept { return state_; }
    [[nodiscard]] T filtered_value() const noexcept { return ema_val_; }
    
    void reset(std::chrono::milliseconds now) noexcept {
        median_count_ = 0;
        median_index_ = 0;
        ema_initialized_ = false;
        state_ = false;
        last_switch_time_ = now;
    }

private:
    Config config_;
    std::array<T, MedianSize> median_buffer_{};
    size_t median_index_{0};
    size_t median_count_{0};
    T ema_val_{0};
    bool ema_initialized_{false};
    bool state_{false};
    std::chrono::milliseconds last_switch_time_{0};
};
