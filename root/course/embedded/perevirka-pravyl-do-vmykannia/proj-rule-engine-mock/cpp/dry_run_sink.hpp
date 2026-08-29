#pragma once

#include <cstddef>
#include <cstdint>
#include <optional>
#include <string>
#include <vector>

#include "contracts.hpp"
#include "rule_engine.hpp"

// Суха прогонка: команди нікуди не йдуть, натомість перевіряються інваріанти.
// Монітор навмисно має ВЛАСНІ межі, а не бере їх у рушія: перевіряльник, що
// користується конфігурацією перевірюваного, підтверджує сам себе.
class DryRunSink : public IActuatorSink {
public:
    struct Limits {
        float pressure_min_bar;
        float pressure_max_bar;
        float temp_critical_c;
    };

    struct LogEntry {
        std::uint32_t timestamp_ms;
        ActuatorState state;
        EngineMode mode;
        std::string violation;
    };

    explicit DryRunSink(Limits lim) : lim_(lim) {}

    // Стенд подає монітору той самий знімок, який бачив рушій: без входів
    // не перевірити перехресних інваріантів («нагрів за небезпечних даних»).
    void note_inputs(const SensorSnapshot& in, EngineMode mode);

    void apply_commands(const ActuatorState& state, std::uint32_t time_ms) override;

    [[nodiscard]] std::size_t violations() const { return violations_; }
    [[nodiscard]] std::uint32_t worst_reaction_ms() const { return worst_reaction_ms_; }
    [[nodiscard]] const std::vector<LogEntry>& log() const { return log_; }
    [[nodiscard]] const ActuatorState& last_commands() const { return last_state_; }
    [[nodiscard]] EngineMode last_mode() const { return last_mode_; }

    void reset_counters();

private:
    [[nodiscard]] bool inputs_unsafe() const;

    Limits lim_;
    SensorSnapshot last_in_{};
    EngineMode last_mode_{EngineMode::Holding};
    ActuatorState last_state_{};
    bool inputs_fresh_{false};
    std::optional<std::uint32_t> unsafe_since_ms_{};
    bool episode_closed_{false};
    std::uint32_t worst_reaction_ms_{0};
    std::size_t violations_{0};
    std::vector<LogEntry> log_;
};
