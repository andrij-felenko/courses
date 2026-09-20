#ifndef GUARDED_TOGGLE_TYPES_H
#define GUARDED_TOGGLE_TYPES_H

#include <cstdint>
#include <string_view>
#include <functional>

// Стани позиції важеля тумблера
enum class SwitchPosition {
    Off,   // Важіль у положенні "Вимкнено"
    On     // Важіль у положенні "Увімкнено"
};

// Стани захисного ковпачка Mollie (Switch Guard)
enum class GuardState {
    Closed, // Ковпачок закритий (блокує важіль)
    Open    // Ковпачок відкритий (важіль доступний для перемикання)
};

// Типи подій безпеки органу керування
enum class SafetyEventType {
    GuardOpened,                // Захисний ковпачок відкрито
    GuardClosed,               // Захисний ковпачок закрито
    SwitchToggled,              // Положення важеля змінено при відкритому ковпачку
    UnauthorizedToggleAttempt, // Спроба несанкціонованого перемикання або виконання дії при закритому ковпачку
    InvalidSignalCombination    // Нештатна або суперечлива комбінація сигналів
};

// Структура даних події органу керування
struct ToggleEventData {
    uint32_t timestamp_ms{0};                                 // Позначка часу події (мс)
    SwitchPosition switch_position{SwitchPosition::Off};     // Поточна позиція важеля
    GuardState guard_state{GuardState::Closed};              // Поточний стан ковпачка
    SafetyEventType event_type{SafetyEventType::GuardClosed}; // Тип згенерованої події
    bool action_allowed{false};                               // Чи дозволено виконання критичних дій
};

// Тип зворотного виклику (callback) для обробки подій
using ToggleEventCallback = std::function<void(const ToggleEventData&)>;

// Перетворення типу події у текстовий рядок для логування
constexpr std::string_view safetyEventToString(SafetyEventType event_type) noexcept {
    switch (event_type) {
        case SafetyEventType::GuardOpened:
            return "Ковпачок відкрито";
        case SafetyEventType::GuardClosed:
            return "Ковпачок закрито";
        case SafetyEventType::SwitchToggled:
            return "Перемикання важеля";
        case SafetyEventType::UnauthorizedToggleAttempt:
            return "Спроба несанкціонованого перемикання";
        case SafetyEventType::InvalidSignalCombination:
            return "Нештатний сигнал";
    }
    return "Невідома подія";
}

#endif // GUARDED_TOGGLE_TYPES_H
