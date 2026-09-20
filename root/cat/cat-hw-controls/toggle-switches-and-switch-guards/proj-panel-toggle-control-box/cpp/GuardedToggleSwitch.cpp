#include "GuardedToggleSwitch.h"
#include <utility>

GuardedToggleSwitch::GuardedToggleSwitch(uint32_t debounce_ms)
    : debounce_ms_(debounce_ms) {}

void GuardedToggleSwitch::setEventCallback(ToggleEventCallback callback) {
    event_callback_ = std::move(callback);
}

void GuardedToggleSwitch::update(bool switch_raw, bool guard_raw, uint32_t current_time_ms) {
    // 1. Неблокувальний дебаунс сигналу ковпачка Mollie
    if (guard_raw != raw_guard_) {
        raw_guard_ = guard_raw;
        guard_last_change_ms_ = current_time_ms;
    } else if (current_time_ms - guard_last_change_ms_ >= debounce_ms_) {
        GuardState new_guard_state = guard_raw ? GuardState::Open : GuardState::Closed;
        if (new_guard_state != guard_state_) {
            guard_state_ = new_guard_state;
            SafetyEventType event = (guard_state_ == GuardState::Open)
                ? SafetyEventType::GuardOpened
                : SafetyEventType::GuardClosed;
            notifyEvent(event, current_time_ms);
        }
    }

    // 2. Неблокувальний дебаунс сигналу важеля тумблера
    if (switch_raw != raw_switch_) {
        raw_switch_ = switch_raw;
        switch_last_change_ms_ = current_time_ms;
    } else if (current_time_ms - switch_last_change_ms_ >= debounce_ms_) {
        SwitchPosition new_switch_pos = switch_raw ? SwitchPosition::On : SwitchPosition::Off;
        if (new_switch_pos != switch_position_) {
            // Перевірка безпеки: перемикання при закритому ковпачку вважається порушенням
            if (guard_state_ == GuardState::Closed) {
                notifyEvent(SafetyEventType::UnauthorizedToggleAttempt, current_time_ms);
            } else {
                switch_position_ = new_switch_pos;
                notifyEvent(SafetyEventType::SwitchToggled, current_time_ms);
            }
        }
    }
}

bool GuardedToggleSwitch::executeCriticalAction(uint32_t current_time_ms) {
    if (guard_state_ == GuardState::Closed) {
        notifyEvent(SafetyEventType::UnauthorizedToggleAttempt, current_time_ms);
        return false;
    }

    if (switch_position_ == SwitchPosition::Off) {
        return false;
    }

    return true;
}

void GuardedToggleSwitch::notifyEvent(SafetyEventType event_type, uint32_t timestamp_ms) {
    if (event_callback_) {
        ToggleEventData event_data;
        event_data.timestamp_ms = timestamp_ms;
        event_data.switch_position = switch_position_;
        event_data.guard_state = guard_state_;
        event_data.event_type = event_type;
        event_data.action_allowed = (guard_state_ == GuardState::Open);
        event_callback_(event_data);
    }
}
