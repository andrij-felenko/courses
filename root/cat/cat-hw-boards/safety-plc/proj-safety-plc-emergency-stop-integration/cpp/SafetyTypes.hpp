#ifndef SAFETY_TYPES_HPP
#define SAFETY_TYPES_HPP

#include <cstdint>
#include <string_view>

namespace safety {

// Стани автомата безпеки контролера (Safety PLC)
enum class SafetyState {
    Safe,               // Безпечний робочий стан, силові виходи увімкнені
    EStopActive,        // Натиснуто кнопку аварійної зупинки E-Stop (канали розімкнені)
    WaitingForReset,    // Аварію усунуто, очікується підтверджене ручне скидання (Reset)
    DiscrepancyFault,   // Апаратна помилка: перевищено час розбіжності між каналами
    EdmFault            // Апаратна помилка: несправність силового контактора або приварювання контактів
};

// Типи помилок функціонального блоку E-Stop
enum class EStopFault {
    None,               // Помилки відсутні
    DiscrepancyTimeout, // Часова розбіжність спрацьовування каналів 1 та 2
    EdmFailure,         // Несправність ланцюга зворотного зв'язку EDM
    InvalidResetSequence// Некоректна послідовність скидання (наприклад, затиснута кнопка Reset)
};

// Стан монітора зворотного зв'язку силових реле (EDM)
enum class EdmFaultState {
    None,               // Ланцюг зворотного зв'язку справний
    ContactWelded,      // Приварювання основних контактів (NC-контакт не замкнувся при вимкненні)
    ContactStuckOpen,   // Заклинювання реле у вимкненому стані (NC-контакт не розімкнувся при увімкненні)
    FeedbackTimeout     // Загальний таймаут невідповідності стану реле
};

// Конфігурація моніторингу зворотного зв'язку (EDM)
struct EdmConfig {
    uint32_t feedback_timeout_ms{250}; // Максимальний допустимий час перемикання контактів реле (мс)
};

// Конфігурація функціонального блоку E-Stop
struct EStopConfig {
    uint32_t discrepancy_time_ms{100};  // Допустимий розкид часу між спрацьовуванням каналів E-Stop (мс)
    bool require_manual_reset{true};    // Вимога переднього фронту сигналу Reset для виходу з аварії
    EdmConfig edm_config{};             // Конфігурація EDM
};

// Допоміжні функції перетворення станів у текстовий вигляд (українською мовою)
constexpr std::string_view to_string(SafetyState state) noexcept {
    switch (state) {
        case SafetyState::Safe:             return "SAFE (Безпечний / Виходи увімкнено)";
        case SafetyState::EStopActive:      return "ESTOP_ACTIVE (Аварійна зупинка)";
        case SafetyState::WaitingForReset:  return "WAITING_FOR_RESET (Очікування скидання)";
        case SafetyState::DiscrepancyFault: return "DISCREPANCY_FAULT (Помилка розбіжності каналів)";
        case SafetyState::EdmFault:         return "EDM_FAULT (Помилка силового реле / EDM)";
    }
    return "UNKNOWN";
}

constexpr std::string_view to_string(EStopFault fault) noexcept {
    switch (fault) {
        case EStopFault::None:                 return "Немає помилки";
        case EStopFault::DiscrepancyTimeout:   return "Перевищено час розбіжності каналів";
        case EStopFault::EdmFailure:           return "Збій зворотного зв'язку EDM";
        case EStopFault::InvalidResetSequence: return "Некоректне скидання (затиснута кнопка)";
    }
    return "UNKNOWN";
}

constexpr std::string_view to_string(EdmFaultState fault) noexcept {
    switch (fault) {
        case EdmFaultState::None:             return "Немає помилки EDM";
        case EdmFaultState::ContactWelded:    return "Приварювання контактів реле (Contact Welded)";
        case EdmFaultState::ContactStuckOpen: return "Заклинювання реле у відкритому стані";
        case EdmFaultState::FeedbackTimeout:  return "Таймаут відповіді зворотного зв'язку";
    }
    return "UNKNOWN";
}

} // namespace safety

#endif // SAFETY_TYPES_HPP
