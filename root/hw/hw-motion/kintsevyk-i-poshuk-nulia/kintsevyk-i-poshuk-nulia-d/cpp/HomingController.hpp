/* 
 * HomingController.hpp
 * Ідіоматична об'єктно-орієнтована C++20 реалізація автомата пошуку нуля
 */

#pragma once

#include <cstdint>
#include <concepts>
#include <chrono>
#include <optional>
#include <expected>

namespace cnc {

using namespace std::chrono_literals;

enum class HomingState : uint8_t {
    Idle = 0,
    Start,
    FastSeek,
    Retract,
    SlowApproach,
    Latch,
    Park,
    Done,
    Fault
};

enum class HomingError : uint8_t {
    None = 0,
    Timeout,
    Overtravel,
    SensorStuck,
    EmergencyStop
};

struct HomingParams {
    float fast_speed_mm_s   {60.0f};  // Швидкий пошук (мм/с)
    float slow_speed_mm_s   {2.0f};   // Прецизійний доїзд (мм/с)
    float retract_dist_mm   {3.0f};   // Дистанція виходу з гістерезису (мм)
    float park_clearance_mm {1.0f};   // Зазор паркування (мм)
    float max_travel_mm     {300.0f}; // Ліміт переміщення (мм)
    float steps_per_mm      {80.0f};  // Кількість мікрокроків на 1 мм
    bool  normally_closed   {true};   // NC контакт (Fail-Safe)
};

// Концепт для апаратного драйвера осі
template <typename T>
concept AxisHardware = requires(T hw, int dir) {
    { hw.read_endstop_raw() } -> std::same_as<bool>;
    { hw.step_pulse(dir) }    -> std::same_as<void>;
    { hw.micros() }           -> std::same_as<uint32_t>;
};

template <AxisHardware Hardware>
class HomingController {
public:
    explicit HomingController(Hardware& hw, const HomingParams& params = {})
        : hw_(hw), params_(params) {}

    void start() noexcept {
        state_ = HomingState::Start;
        error_ = HomingError::None;
        current_step_ = 0;
    }

    [[nodiscard]] bool is_busy() const noexcept {
        return state_ != HomingState::Idle && 
               state_ != HomingState::Done && 
               state_ != HomingState::Fault;
    }

    [[nodiscard]] bool is_successful() const noexcept {
        return state_ == HomingState::Done;
    }

    [[nodiscard]] HomingState state() const noexcept { return state_; }
    [[nodiscard]] HomingError error() const noexcept { return error_; }
    [[nodiscard]] int32_t current_step() const noexcept { return current_step_; }

    // Головний неблокуючий цикл оновлення
    void poll() noexcept {
        if (!is_busy()) return;

        const uint32_t now = hw_.micros();

        switch (state_) {
            case HomingState::Start:
                handle_start(now);
                break;

            case HomingState::FastSeek:
                handle_fast_seek(now);
                break;

            case HomingState::Retract:
                handle_retract(now);
                break;

            case HomingState::SlowApproach:
                handle_slow_approach(now);
                break;

            case HomingState::Latch:
                handle_latch();
                break;

            case HomingState::Park:
                handle_park(now);
                break;

            default:
                fail(HomingError::Timeout);
                break;
        }
    }

private:
    [[nodiscard]] bool is_endstop_active() const noexcept {
        const bool raw = hw_.read_endstop_raw();
        // Для NC активний стан (упор/обрив) — це розрив ланцюга (HIGH при підтяжці до VCC)
        return params_.normally_closed ? raw : !raw;
    }

    [[nodiscard]] static constexpr uint32_t speed_to_interval(float speed_mm_s, float steps_per_mm) noexcept {
        if (speed_mm_s < 0.1f) speed_mm_s = 0.1f;
        return static_cast<uint32_t>(1'000'000.0f / (speed_mm_s * steps_per_mm));
    }

    void fail(HomingError err) noexcept {
        state_ = HomingState::Fault;
        error_ = err;
    }

    void handle_start(uint32_t now) noexcept {
        if (is_endstop_active()) {
            state_ = HomingState::Retract;
            step_interval_us_ = speed_to_interval(params_.fast_speed_mm_s * 0.5f, params_.steps_per_mm);
            target_step_ = current_step_ + static_cast<int32_t>(params_.retract_dist_mm * params_.steps_per_mm);
        } else {
            state_ = HomingState::FastSeek;
            step_interval_us_ = speed_to_interval(params_.fast_speed_mm_s, params_.steps_per_mm);
            limit_steps_ = static_cast<int32_t>(params_.max_travel_mm * 1.2f * params_.steps_per_mm);
        }
        last_step_us_ = now;
    }

    void handle_fast_seek(uint32_t now) noexcept {
        if (now - last_step_us_ < step_interval_us_) return;
        last_step_us_ = now;

        if (is_endstop_active()) {
            state_ = HomingState::Retract;
            step_interval_us_ = speed_to_interval(params_.fast_speed_mm_s * 0.5f, params_.steps_per_mm);
            target_step_ = current_step_ + static_cast<int32_t>(params_.retract_dist_mm * params_.steps_per_mm);
        } else {
            hw_.step_pulse(-1);
            --current_step_;

            if (-current_step_ > limit_steps_) {
                fail(HomingError::Overtravel);
            }
        }
    }

    void handle_retract(uint32_t now) noexcept {
        if (now - last_step_us_ < step_interval_us_) return;
        last_step_us_ = now;

        if (current_step_ < target_step_) {
            hw_.step_pulse(+1);
            ++current_step_;
        } else {
            if (is_endstop_active()) {
                fail(HomingError::SensorStuck);
            } else {
                state_ = HomingState::SlowApproach;
                step_interval_us_ = speed_to_interval(params_.slow_speed_mm_s, params_.steps_per_mm);
                limit_steps_ = static_cast<int32_t>(params_.retract_dist_mm * 2.0f * params_.steps_per_mm);
            }
        }
    }

    void handle_slow_approach(uint32_t now) noexcept {
        if (now - last_step_us_ < step_interval_us_) return;
        last_step_us_ = now;

        if (is_endstop_active()) {
            state_ = HomingState::Latch;
        } else {
            hw_.step_pulse(-1);
            --current_step_;

            if (target_step_ - current_step_ > limit_steps_) {
                fail(HomingError::Timeout);
            }
        }
    }

    void handle_latch() noexcept {
        current_step_ = 0; // Апаратна точка нуля зафіксована
        target_step_ = static_cast<int32_t>(params_.park_clearance_mm * params_.steps_per_mm);
        step_interval_us_ = speed_to_interval(params_.fast_speed_mm_s * 0.5f, params_.steps_per_mm);
        state_ = HomingState::Park;
    }

    void handle_park(uint32_t now) noexcept {
        if (now - last_step_us_ < step_interval_us_) return;
        last_step_us_ = now;

        if (current_step_ < target_step_) {
            hw_.step_pulse(+1);
            ++current_step_;
        } else {
            state_ = HomingState::Done;
        }
    }

    Hardware&     hw_;
    HomingParams  params_;
    HomingState   state_            {HomingState::Idle};
    HomingError   error_            {HomingError::None};
    int32_t       current_step_     {0};
    int32_t       target_step_      {0};
    int32_t       limit_steps_      {0};
    uint32_t      step_interval_us_ {1000};
    uint32_t      last_step_us_     {0};
};

} // namespace cnc
