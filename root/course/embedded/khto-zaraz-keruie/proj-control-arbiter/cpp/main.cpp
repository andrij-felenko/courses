#include <iostream>
#include <array>
#include <chrono>
#include <cmath>
#include <algorithm>
#include <span>

namespace embedded::control {

using Microseconds = std::chrono::microseconds;

enum class SourceId : uint8_t {
    Failsafe = 0,
    RcPilot = 1,
    Offboard = 2,
    GcsMission = 3,
    None = 255
};

constexpr size_t SourceCount = 4;

struct Setpoint {
    Microseconds timestamp{0};
    std::array<float, 4> channels{0.0f, 0.0f, 0.0f, 0.0f}; // Roll, Pitch, Yaw, Thrust
    bool valid{false};
};

struct SourceConfig {
    Microseconds timeout{std::chrono::milliseconds(500)};
    float stick_deadband{0.08f};
    std::array<float, 4> max_slew_rate{6.0f, 6.0f, 10.0f, 3.0f}; // од/с на канал
    bool allow_stick_override{true};
};

class ControlArbiter {
public:
    ControlArbiter() noexcept {
        for (auto& slot : slots_) {
            slot.config = SourceConfig{};
        }
    }

    void submit_setpoint(SourceId id, const Setpoint& sp, Microseconds now) noexcept {
        auto idx = static_cast<size_t>(id);
        if (idx >= SourceCount) return;
        slots_[idx].raw_sp = sp;
        slots_[idx].last_heartbeat = now;
        slots_[idx].is_active = true;
        slots_[idx].is_timed_out = false;
    }

    Setpoint evaluate(Microseconds now) noexcept {
        // 1. Оновлення таймаутів
        for (auto& slot : slots_) {
            if (slot.is_active) {
                if ((now - slot.last_heartbeat) > slot.config.timeout) {
                    slot.is_timed_out = true;
                    slot.is_active = false;
                }
            }
        }

        // 2. Ієрархія авторитету
        SourceId selected = SourceId::None;

        if (is_slot_available(SourceId::Failsafe)) {
            selected = SourceId::Failsafe;
        } else if (is_slot_available(SourceId::RcPilot)) {
            bool sticks_moved = check_stick_deflection(slots_[static_cast<size_t>(SourceId::RcPilot)]);
            if (sticks_moved) {
                selected = SourceId::RcPilot;
            } else if (slots_[static_cast<size_t>(SourceId::Offboard)].is_timed_out &&
                       slots_[static_cast<size_t>(SourceId::GcsMission)].is_timed_out) {
                selected = SourceId::RcPilot;
            }
        }

        if (selected == SourceId::None && is_slot_available(SourceId::Offboard)) {
            selected = SourceId::Offboard;
        }

        if (selected == SourceId::None && is_slot_available(SourceId::GcsMission)) {
            selected = SourceId::GcsMission;
        }

        if (selected != active_source_) {
            previous_source_ = active_source_;
            active_source_ = selected;
            transitions_++;
        }

        // 3. Безударне обмеження швидкості зміни уставки (Slew Rate)
        float dt = 0.0025f;
        if (last_eval_time_.count() > 0 && now > last_eval_time_) {
            dt = std::chrono::duration<float>(now - last_eval_time_).count();
            dt = std::clamp(dt, 0.0001f, 0.1f);
        }
        last_eval_time_ = now;

        if (selected != SourceId::None && slots_[static_cast<size_t>(selected)].raw_sp.valid) {
            const auto& target = slots_[static_cast<size_t>(selected)].raw_sp;
            const auto& cfg = slots_[static_cast<size_t>(selected)].config;

            for (size_t i = 0; i < 4; ++i) {
                float target_val = target.channels[i];
                float current_val = smoothed_output_.channels[i];
                float max_delta = cfg.max_slew_rate[i] * dt;
                float delta = std::clamp(target_val - current_val, -max_delta, max_delta);
                smoothed_output_.channels[i] = current_val + delta;
            }
            smoothed_output_.valid = true;
        } else {
            smoothed_output_.channels = {0.0f, 0.0f, 0.0f, 0.0f};
            smoothed_output_.valid = false;
        }

        smoothed_output_.timestamp = now;
        return smoothed_output_;
    }

    [[nodiscard]] SourceId active_source() const noexcept { return active_source_; }
    [[nodiscard]] uint32_t transition_count() const noexcept { return transitions_; }

private:
    struct Slot {
        Setpoint raw_sp{};
        Microseconds last_heartbeat{0};
        SourceConfig config{};
        bool is_active{false};
        bool is_timed_out{true};
    };

    [[nodiscard]] bool is_slot_available(SourceId id) const noexcept {
        const auto& s = slots_[static_cast<size_t>(id)];
        return s.is_active && !s.is_timed_out;
    }

    [[nodiscard]] static bool check_stick_deflection(const Slot& slot) noexcept {
        if (!slot.is_active || slot.is_timed_out || !slot.raw_sp.valid) return false;
        float r = std::abs(slot.raw_sp.channels[0]);
        float p = std::abs(slot.raw_sp.channels[1]);
        float y = std::abs(slot.raw_sp.channels[2]);
        float db = slot.config.stick_deadband;
        return (r > db) || (p > db) || (y > db);
    }

    std::array<Slot, SourceCount> slots_{};
    SourceId active_source_{SourceId::None};
    SourceId previous_source_{SourceId::None};
    Setpoint smoothed_output_{};
    Microseconds last_eval_time_{0};
    uint32_t transitions_{0};
};

} // namespace embedded::control

int main() {
    using namespace embedded::control;
    using namespace std::chrono_literals;

    ControlArbiter arbiter;
    auto now = 1000000us;

    std::cout << "=== C++ СИМУЛЯЦІЯ ДИСПЕТЧЕРА ПРІОРИТЕТІВ ДЖЕРЕЛ КЕРУВАННЯ ===\n\n";

    // 1. Offboard уставка
    Setpoint offboard_sp{
        .timestamp = now,
        .channels = {0.35f, 0.0f, 0.0f, 0.55f},
        .valid = true
    };
    arbiter.submit_setpoint(SourceId::Offboard, offboard_sp, now);

    auto out = arbiter.evaluate(now);
    std::cout << "[1.00s] Активне джерело: " << static_cast<int>(arbiter.active_source())
              << " | Roll: " << out.channels[0] << ", Thrust: " << out.channels[3] << "\n";

    // 2. Перехоплення стіками пілота
    now += 50ms;
    Setpoint rc_sp{
        .timestamp = now,
        .channels = {0.0f, 0.78f, 0.0f, 0.70f},
        .valid = true
    };
    arbiter.submit_setpoint(SourceId::RcPilot, rc_sp, now);
    out = arbiter.evaluate(now);
    std::cout << "[1.05s] Пілот перехопив керування! Джерело: " 
              << static_cast<int>(arbiter.active_source())
              << " | Pitch out: " << out.channels[1] << "\n";

    // Плавний вихід на цільове значення
    for (int i = 0; i < 4; ++i) {
        now += 25ms;
        arbiter.submit_setpoint(SourceId::RcPilot, rc_sp, now);
        out = arbiter.evaluate(now);
        std::cout << "  [+25ms] Slew rate: Pitch out = " << out.channels[1] << "\n";
    }

    return 0;
}
