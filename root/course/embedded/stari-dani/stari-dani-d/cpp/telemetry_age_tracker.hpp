/* telemetry_age_tracker.hpp — Ідіоматичний C++20 модуль моніторингу віку телеметрії */
#pragma once

#include <cstdint>
#include <string_view>
#include <array>
#include <algorithm>
#include <concepts>

namespace telemetry {

inline constexpr uint8_t RecoveryConsecutivePackets = 3;

enum class State : uint8_t {
    Fresh,     // 0..500 мс: свіжі дані, 100% контраст
    Degraded,  // 500..2000 мс: попередня втрата, збліднення, жовта плашка
    Stale      // > 2000 мс: недійсні дані, червоний хрест, очищення
};

enum class BorderColor : uint8_t {
    Normal,
    WarningAmber,
    StaleRed
};

struct VisualState {
    float       alpha_opacity{0.0f};
    BorderColor border_color{BorderColor::StaleRed};
    bool        cross_out_required{true};
    bool        show_age_badge{false};
    State       state{State::Stale};
    uint32_t    age_ms{0};
    
    // Фіксований буфер для уникнення динамічного виділення пам'яті (malloc/new)
    std::array<char, 16> age_str_buf{};
    std::string_view     age_text{};
};

template <typename T>
class TelemetrySlot {
public:
    constexpr TelemetrySlot(uint32_t warn_timeout_ms = 500, 
                            uint32_t stale_timeout_ms = 2000) noexcept
        : warn_timeout_ms_(warn_timeout_ms),
          stale_timeout_ms_(stale_timeout_ms) {}

    void update(const T& value, uint8_t sequence, uint32_t onboard_boot_ms, uint32_t now_monotonic_ms) noexcept {
        // Якщо бортовий час не збільшується при зростанні sequence — датчик на борті завис
        if (has_received_first_ && onboard_boot_ms == last_onboard_boot_ms_ && sequence != last_sequence_) {
            is_sensor_frozen_ = true;
            consecutive_good_frames_ = 0;
            return;
        }

        value_ = value;
        last_sequence_ = sequence;
        last_onboard_boot_ms_ = onboard_boot_ms;
        last_rx_monotonic_ms_ = now_monotonic_ms;
        has_received_first_ = true;
        is_sensor_frozen_ = false;

        if (consecutive_good_frames_ < RecoveryConsecutivePackets) {
            ++consecutive_good_frames_;
        }
    }

    [[nodiscard]] VisualState get_visual_state(uint32_t now_monotonic_ms) const noexcept {
        VisualState vs;

        if (!has_received_first_ || is_sensor_frozen_) {
            vs.state = State::Stale;
            vs.alpha_opacity = 0.35f;
            vs.border_color = BorderColor::StaleRed;
            vs.cross_out_required = true;
            vs.show_age_badge = true;
            vs.age_ms = is_sensor_frozen_ ? stale_timeout_ms_ + 1000 : 0xFFFFFFFFU;
            format_age_str(vs, vs.age_ms);
            return vs;
        }

        // Безпечне віднімання беззнакових чисел (стійке до переповнення таймера uint32_t)
        const uint32_t age = now_monotonic_ms - last_rx_monotonic_ms_;
        vs.age_ms = age;

        // Потрібна серія з RecoveryConsecutivePackets свіжих пакетів для виходу з тривоги
        const bool is_fully_recovered = (consecutive_good_frames_ >= RecoveryConsecutivePackets);

        if (age <= warn_timeout_ms_ && is_fully_recovered) {
            vs.state = State::Fresh;
            vs.alpha_opacity = 1.0f;
            vs.border_color = BorderColor::Normal;
            vs.cross_out_required = false;
            vs.show_age_badge = false;
            vs.age_text = "FRESH";
        } else if (age <= stale_timeout_ms_) {
            vs.state = State::Degraded;
            // Плавне зниження контрасту від 0.85f до 0.45f пропорційно до віку
            const float factor = static_cast<float>(age - warn_timeout_ms_) / 
                                 static_cast<float>(stale_timeout_ms_ - warn_timeout_ms_);
            vs.alpha_opacity = std::clamp(0.85f - (factor * 0.40f), 0.45f, 0.85f);
            vs.border_color = BorderColor::WarningAmber;
            vs.cross_out_required = false;
            vs.show_age_badge = true;
            format_age_str(vs, age);
        } else {
            vs.state = State::Stale;
            vs.alpha_opacity = 0.35f;
            vs.border_color = BorderColor::StaleRed;
            vs.cross_out_required = true;
            vs.show_age_badge = true;
            format_age_str(vs, age);
        }

        return vs;
    }

    [[nodiscard]] const T* get_valid_value(uint32_t now_monotonic_ms) const noexcept {
        if (!has_received_first_ || is_sensor_frozen_) {
            return nullptr;
        }
        if ((now_monotonic_ms - last_rx_monotonic_ms_) > stale_timeout_ms_) {
            return nullptr;
        }
        return &value_;
    }

private:
    static void format_age_str(VisualState& vs, uint32_t age_ms) noexcept {
        if (age_ms >= 10000) {
            vs.age_str_buf = {'>', '9', '.', '9', 's', '\0'};
        } else {
            const uint32_t sec = age_ms / 1000;
            const uint32_t tenths = (age_ms % 1000) / 100;
            vs.age_str_buf[0] = '+';
            vs.age_str_buf[1] = static_cast<char>('0' + sec);
            vs.age_str_buf[2] = '.';
            vs.age_str_buf[3] = static_cast<char>('0' + tenths);
            vs.age_str_buf[4] = 's';
            vs.age_str_buf[5] = '\0';
        }
        vs.age_text = std::string_view(vs.age_str_buf.data());
    }

    T        value_{};
    uint32_t last_rx_monotonic_ms_{0};
    uint32_t last_onboard_boot_ms_{0};
    uint8_t  last_sequence_{0};
    uint8_t  consecutive_good_frames_{0};
    bool     has_received_first_{false};
    bool     is_sensor_frozen_{false};
    
    uint32_t warn_timeout_ms_{500};
    uint32_t stale_timeout_ms_{2000};
};

} // namespace telemetry
