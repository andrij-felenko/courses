// app/state_machine.hpp — автомат режимів логера.
// Класу нічого не відомо ні про шину, ні про давач: на вхід подія, на
// вихід — назва дії. Через це весь набір переходів перевіряється на
// комп'ютері розробника за мілісекунди, без плати й термофена.
#pragma once

#include "app/events.hpp"

#include <cstdint>
#include <string_view>

namespace app {

enum class State : std::uint8_t {
    Boot = 0,
    Idle,      // давачі підняті, запис призупинено
    Sampling,  // штатний збір даних
    Alarm,     // перевищено поріг, запис триває
    Fault      // давач не відповідає, потрібне втручання
};

enum class Action : std::uint8_t {
    None = 0,
    StartSampling,
    StopSampling,
    SampleSensors,
    RaiseAlarm,
    ClearAlarm,
    EnterFault,
    Recover
};

class StateMachine {
public:
    explicit StateMachine(std::uint32_t fault_limit) noexcept
        : fault_limit_{fault_limit == 0 ? 1 : fault_limit} {}

    // Єдина точка переходів.
    [[nodiscard]] Action dispatch(const SystemEvent& event);

    [[nodiscard]] State state() const noexcept { return state_; }
    [[nodiscard]] hal::Millis state_since() const noexcept { return state_since_; }
    [[nodiscard]] std::uint32_t consecutive_faults() const noexcept { return faults_; }

private:
    void enter(State next, hal::Millis now);

    State         state_{State::Boot};
    hal::Millis   state_since_{0};
    std::uint32_t faults_{0};
    std::uint32_t fault_limit_;
};

[[nodiscard]] constexpr std::string_view to_string(State s) noexcept
{
    switch (s) {
    case State::Boot:     return "BOOT";
    case State::Idle:     return "IDLE";
    case State::Sampling: return "SAMPLING";
    case State::Alarm:    return "ALARM";
    case State::Fault:    return "FAULT";
    }
    return "?";
}

[[nodiscard]] constexpr std::string_view to_string(Action a) noexcept
{
    switch (a) {
    case Action::None:          return "NONE";
    case Action::StartSampling: return "START";
    case Action::StopSampling:  return "STOP";
    case Action::SampleSensors: return "SAMPLE";
    case Action::RaiseAlarm:    return "ALARM";
    case Action::ClearAlarm:    return "CLEAR";
    case Action::EnterFault:    return "FAULT";
    case Action::Recover:       return "RECOVER";
    }
    return "?";
}

} // namespace app
