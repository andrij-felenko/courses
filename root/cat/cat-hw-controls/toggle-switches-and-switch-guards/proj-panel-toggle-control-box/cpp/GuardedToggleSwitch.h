#ifndef GUARDED_TOGGLE_SWITCH_H
#define GUARDED_TOGGLE_SWITCH_H

#include "GuardedToggleTypes.h"
#include <cstdint>

// Клас драйвера тумблера із захисним ковпачком Mollie
class GuardedToggleSwitch {
public:
    // Конструктор: приймає параметр тривалості дебаунсу у мілісекундах
    explicit GuardedToggleSwitch(uint32_t debounce_ms = 20);

    // Встановлення функціонального callback для обробки подій
    void setEventCallback(ToggleEventCallback callback);

    // Метод неблокувального оновлення станів (опитування цифрових сигналів)
    // switch_raw: true = HIGH (On), false = LOW (Off)
    // guard_raw: true = HIGH (Open), false = LOW (Closed)
    void update(bool switch_raw, bool guard_raw, uint32_t current_time_ms);

    // Спроба виконання критичної команди, прив'язаної до тумблера
    bool executeCriticalAction(uint32_t current_time_ms);

    // Геттери поточного стану
    [[nodiscard]] SwitchPosition getSwitchPosition() const noexcept { return switch_position_; }
    [[nodiscard]] GuardState getGuardState() const noexcept { return guard_state_; }
    [[nodiscard]] bool isActionAllowed() const noexcept { return guard_state_ == GuardState::Open; }

private:
    uint32_t debounce_ms_{20};

    // Фільтровані стани
    SwitchPosition switch_position_{SwitchPosition::Off};
    GuardState guard_state_{GuardState::Closed};

    // Сирі стани для дебаунсу
    bool raw_switch_{false};
    bool raw_guard_{false};

    // Таймери дебаунсу
    uint32_t switch_last_change_ms_{0};
    uint32_t guard_last_change_ms_{0};

    ToggleEventCallback event_callback_{nullptr};

    void notifyEvent(SafetyEventType event_type, uint32_t timestamp_ms);
};

#endif // GUARDED_TOGGLE_SWITCH_H
