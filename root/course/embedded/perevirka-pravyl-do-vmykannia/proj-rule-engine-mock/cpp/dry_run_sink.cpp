#include "dry_run_sink.hpp"

#include <algorithm>
#include <cmath>
#include <format>
#include <iostream>
#include <stdexcept>
#include <utility>

void DryRunSink::note_inputs(const SensorSnapshot& in, EngineMode mode) {
    last_in_ = in;
    last_mode_ = mode;
    inputs_fresh_ = true;
}

bool DryRunSink::inputs_unsafe() const {
    return last_in_.emergency_stop_btn ||
           last_in_.sensor_fault ||
           !std::isfinite(last_in_.temperature_c) ||
           !std::isfinite(last_in_.pressure_bar) ||
           last_in_.pressure_bar < lim_.pressure_min_bar ||
           last_in_.pressure_bar > lim_.pressure_max_bar ||
           last_in_.temperature_c >= lim_.temp_critical_c ||
           !last_in_.flow_detected;
}

void DryRunSink::apply_commands(const ActuatorState& state, std::uint32_t time_ms) {
    if (!inputs_fresh_) {
        // Без свіжого знімка монітор судив би команди за чужими входами —
        // це гірше за відсутню перевірку, бо виглядає як пройдений тест.
        throw std::logic_error("стенд не передав монітору вхідний знімок перед командами");
    }
    inputs_fresh_ = false;
    last_state_ = state;

    const bool heat = heaters_on(state);
    std::string violation;

    // Інваріант 1: нагрів без помпи — це сухий ТЕН, найдорожча помилка таблиці.
    if (heat && !state.circulation_pump) {
        violation = "ТЕНи увімкнені без помпи — сухий нагрів";
    }

    // Інваріант 2 і заразом вимірювання затримки реакції: скільки мілісекунд
    // нагрів тримався після того, як входи стали небезпечними.
    const bool unsafe = inputs_unsafe();
    if (unsafe) {
        if (!unsafe_since_ms_) {
            unsafe_since_ms_ = time_ms;
            episode_closed_ = false;
        }
        const std::uint32_t elapsed_ms = time_ms - *unsafe_since_ms_;
        if (heat) {
            worst_reaction_ms_ = std::max(worst_reaction_ms_, elapsed_ms);
            if (violation.empty()) {
                violation = "нагрів триває за небезпечних вхідних даних";
            }
        } else if (!episode_closed_) {
            worst_reaction_ms_ = std::max(worst_reaction_ms_, elapsed_ms);
            episode_closed_ = true;
        }
    } else {
        unsafe_since_ms_.reset();
        episode_closed_ = false;
    }

    if (!violation.empty()) {
        ++violations_;
        std::cout << std::format("  [{:>7} мс] ПОРУШЕННЯ ІНВАРІАНТА: {}\n", time_ms, violation);
    }
    log_.push_back(LogEntry{time_ms, state, last_mode_, std::move(violation)});
}

void DryRunSink::reset_counters() {
    log_.clear();
    violations_ = 0;
    worst_reaction_ms_ = 0;
    unsafe_since_ms_.reset();
    episode_closed_ = false;
}
