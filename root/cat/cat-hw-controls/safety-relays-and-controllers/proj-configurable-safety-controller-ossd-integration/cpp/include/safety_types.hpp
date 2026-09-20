#ifndef SAFETY_TYPES_HPP
#define SAFETY_TYPES_HPP

#include <cstdint>
#include <chrono>
#include <string_view>

namespace safety {

// Стани контролера безпеки згідно з ISO 13849-1 та IEC 62061
enum class SafetyState {
    Safe,           // Захисна зона замкнена, силові виходи увімкнені
    Muting,         // Тимчасове безпечне приглушення захисної зони
    BlankingActive, // Режим фіксованого/плаваючого маскування балок
    Tripped,        // Зона порушена (аварійне відключення виходів)
    Fault           // Апаратний збій або помилка неузгодженості каналів
};

// Режими перезапуску після спрацьовування захисту
enum class ResetMode {
    Manual, // Ручний перезапуск натисканням кнопки Reset
    Auto    // Автоматичний перезапуск при відновленні сигналів
};

// Коди апаратних та часових помилок
enum class FaultCode {
    None,               // Помилки відсутні
    DiscrepancyFault,   // Перевищено час розходження між OSSD1 та OSSD2
    CrossFault,         // Виявлено коротке замикання між каналами
    MutingTimeout,      // Перевищено часовий ліміт приглушення зони
    MutingSequenceError,// Некоректна послідовність спрацьовування датчиків Muting
    HardwareFailure     // Збій зчитування входів або зворотного зв'язку EDM
};

// Конфігураційні часові параметри контролера
struct SafetyConfig {
    uint32_t discrepancy_time_ms{200}; // Допустиме розходження між каналами (мс)
    uint32_t muting_timeout_ms{5000};  // Максимальна тривалість Muting (мс)
    ResetMode reset_mode{ResetMode::Manual};
    uint32_t blanking_mask{0x0000};    // Бітова маска приглушених променів
};

// Перетворення коду помилки у текстове повідомлення українською
constexpr std::string_view fault_code_to_string(FaultCode code) {
    switch (code) {
        case FaultCode::None:                return "Помилок немає";
        case FaultCode::DiscrepancyFault:    return "Перевищено час розходження каналів OSSD";
        case FaultCode::CrossFault:          return "Виявлено перехресне коротке замикання";
        case FaultCode::MutingTimeout:       return "Перевищено таймаут режиму Muting";
        case FaultCode::MutingSequenceError: return "Помилка послідовності датчиків Muting";
        case FaultCode::HardwareFailure:     return "Апаратна відмова або збій EDM";
        default:                             return "Невідома помилка";
    }
}

} // namespace safety

#endif // SAFETY_TYPES_HPP
