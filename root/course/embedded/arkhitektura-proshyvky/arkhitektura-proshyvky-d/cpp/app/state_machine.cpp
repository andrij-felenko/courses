// app/state_machine.cpp — таблиця переходів логера.
// Жодного включення з hal/ або bsp/: файл однаково збирається хостовим
// компілятором і кроскомпілятором arm-none-eabi-g++.
#include "app/state_machine.hpp"

namespace app {

void StateMachine::enter(State next, hal::Millis now)
{
    if (state_ != next) {
        state_ = next;
        state_since_ = now;
    }
}

Action StateMachine::dispatch(const SystemEvent& event)
{
    const auto now = event.timestamp;

    // Відмова давача рахується в будь-якому стані: одна невдача — випадковість
    // на шині, п'ять поспіль — обрив шлейфа, і про це має знати обслуга.
    if (event.id == EventId::SensorFault) {
        ++faults_;
        if (faults_ >= fault_limit_ && state_ != State::Fault) {
            enter(State::Fault, now);
            return Action::EnterFault;
        }
        return Action::None;
    }

    if (event.id == EventId::SensorDataReady) {
        faults_ = 0;
        if (state_ == State::Fault) {
            enter(State::Sampling, now);
            return Action::Recover;
        }
        return Action::None;
    }

    switch (state_) {

    case State::Boot:
        if (event.id == EventId::Tick) {
            enter(State::Sampling, now);
            return Action::StartSampling;
        }
        return Action::None;

    case State::Idle:
        if (event.id == EventId::ButtonClick) {
            enter(State::Sampling, now);
            return Action::StartSampling;
        }
        return Action::None;

    case State::Sampling:
        switch (event.id) {
        case EventId::Tick:
            return Action::SampleSensors;
        case EventId::ButtonClick:
            enter(State::Idle, now);
            return Action::StopSampling;
        case EventId::AlarmOvertemp:
        case EventId::AlarmVibration:
            enter(State::Alarm, now);
            return Action::RaiseAlarm;
        default:
            return Action::None;
        }

    case State::Alarm:
        switch (event.id) {
        case EventId::Tick:
            // У тривозі вимірювання не спиняються: саме ці дані потім
            // розбиратимуть, з'ясовуючи, чому став насос.
            return Action::SampleSensors;
        case EventId::AlarmCleared:
            enter(State::Sampling, now);
            return Action::ClearAlarm;
        default:
            return Action::None;
        }

    case State::Fault:
        // Пробуємо опитати давач знову; вихід зі стану лежить у гілці
        // EventId::SensorDataReady вище.
        return (event.id == EventId::Tick) ? Action::SampleSensors : Action::None;
    }

    return Action::None;
}

} // namespace app
