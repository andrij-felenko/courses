#include "contactor_timer.hpp"

#if defined(ARDUINO)
#include <Arduino.h>
#else
#include <chrono>
static uint32_t simulated_millis() {
    using namespace std::chrono;
    return static_cast<uint32_t>(duration_cast<milliseconds>(steady_clock::now().time_since_epoch()).count());
}
#endif

ContactorTimer::ContactorTimer(ContactorPinConfig phase_a, ContactorPinConfig phase_b, uint32_t dead_time_ms)
    : phase_a_(phase_a), phase_b_(phase_b), dead_time_ms_(dead_time_ms),
      active_phase_(0), pending_phase_(0), switch_timestamp_ms_(0), state_(State::IDLE) {}

void ContactorTimer::begin() {
    setCoilState(phase_a_.coil_pin, false);
    setCoilState(phase_b_.coil_pin, false);
    active_phase_ = 0;
    state_ = State::IDLE;
}

bool ContactorTimer::readNcState(uint8_t pin) const {
#if defined(ARDUINO)
    return digitalRead(pin) == HIGH;
#else
    (void)pin;
    return true;
#endif
}

void ContactorTimer::setCoilState(uint8_t pin, bool enabled) {
#if defined(ARDUINO)
    digitalWrite(pin, enabled ? HIGH : LOW);
#else
    (void)pin;
    (void)enabled;
#endif
}

uint32_t ContactorTimer::getSystemMillis() const {
#if defined(ARDUINO)
    return millis();
#else
    return simulated_millis();
#endif
}

bool ContactorTimer::selectPhase(uint8_t target_phase) {
    if (state_ != State::IDLE || target_phase == active_phase_) {
        return false;
    }
    pending_phase_ = target_phase;
    if (active_phase_ == 1) {
        setCoilState(phase_a_.coil_pin, false);
    } else if (active_phase_ == 2) {
        setCoilState(phase_b_.coil_pin, false);
    }
    switch_timestamp_ms_ = getSystemMillis();
    state_ = State::WAITING_RELEASE;
    return true;
}

void ContactorTimer::update() {
    switch (state_) {
    case State::IDLE:
        break;

    case State::WAITING_RELEASE: {
        uint8_t check_pin = (active_phase_ == 1) ? phase_a_.nc_feedback_pin : phase_b_.nc_feedback_pin;
        if (active_phase_ == 0 || readNcState(check_pin)) {
            switch_timestamp_ms_ = getSystemMillis();
            state_ = State::DEAD_TIME;
        }
        break;
    }

    case State::DEAD_TIME:
        if (getSystemMillis() - switch_timestamp_ms_ >= dead_time_ms_) {
            state_ = State::ENABLING;
        }
        break;

    case State::ENABLING:
        if (pending_phase_ == 1) {
            setCoilState(phase_a_.coil_pin, true);
        } else if (pending_phase_ == 2) {
            setCoilState(phase_b_.coil_pin, true);
        }
        active_phase_ = pending_phase_;
        pending_phase_ = 0;
        state_ = State::IDLE;
        break;
    }
}

uint8_t ContactorTimer::getActivePhase() const {
    return active_phase_;
}
