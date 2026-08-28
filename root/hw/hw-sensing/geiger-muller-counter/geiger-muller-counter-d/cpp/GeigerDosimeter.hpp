// GeigerDosimeter.hpp — Ідіоматична реалізація на сучасному C++20
#pragma once

#include <array>
#include <atomic>
#include <cmath>
#include <cstdint>
#include <numeric>
#include <span>

namespace sensing {

struct DosimeterConfig {
    float dead_time_sec{0.000100f};  // 100 мкс для СБМ-20
    float cpm_per_usv_h{153.84f};     // ~154 CPM = 1 мкЗв/год (Cs-137)
};

struct RadiationReading {
    float dose_rate_usv_h{0.0f};
    float cpm{0.0f};
    float statistical_error_pct{100.0f};
    uint32_t total_counts{0};
};

template <std::size_t HistorySeconds = 60>
class GeigerDosimeter {
public:
    explicit constexpr GeigerDosimeter(DosimeterConfig config) noexcept
        : config_(config) {}

    // Викликається з ISR переривання пін-тригера
    void on_pulse_isr() noexcept {
        isr_pulses_.fetch_add(1, std::memory_order_relaxed);
    }

    // Періодичний виклик із частотою 1 Гц
    void tick_1hz() noexcept {
        const auto new_pulses = isr_pulses_.exchange(0, std::memory_order_relaxed);
        total_lifetime_counts_ += new_pulses;

        history_[history_head_] = static_cast<uint16_t>(new_pulses);
        history_head_ = (history_head_ + 1) % HistorySeconds;

        if (active_seconds_ < HistorySeconds) {
            ++active_seconds_;
        }

        const uint32_t window_sum = std::accumulate(
            history_.begin(), history_.begin() + active_seconds_, 0u
        );

        const float measured_cps = static_cast<float>(window_sum) / static_cast<float>(active_seconds_);

        // Корекція мертвого часу непаралізовного детектора
        const float denom = 1.0f - (measured_cps * config_.dead_time_sec);
        const float corrected_cps = (denom > 0.05f) ? (measured_cps / denom) : (measured_cps / 0.05f);

        const float cpm = corrected_cps * 60.0f;
        const float dose_rate = cpm / config_.cpm_per_usv_h;
        const float err_pct = (window_sum > 0)
            ? (100.0f / std::sqrt(static_cast<float>(window_sum)))
            : 100.0f;

        current_reading_ = RadiationReading{
            .dose_rate_usv_h = dose_rate,
            .cpm = cpm,
            .statistical_error_pct = err_pct,
            .total_counts = total_lifetime_counts_
        };
    }

    [[nodiscard]] RadiationReading get_reading() const noexcept {
        return current_reading_;
    }

    [[nodiscard]] constexpr std::size_t window_size() const noexcept {
        return HistorySeconds;
    }

private:
    DosimeterConfig config_;
    std::atomic<uint32_t> isr_pulses_{0};
    std::array<uint16_t, HistorySeconds> history_{};
    std::size_t history_head_{0};
    std::size_t active_seconds_{0};
    uint32_t total_lifetime_counts_{0};
    RadiationReading current_reading_{};
};

} // namespace sensing
