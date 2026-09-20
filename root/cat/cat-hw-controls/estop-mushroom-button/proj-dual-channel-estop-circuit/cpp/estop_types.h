#ifndef ESTOP_TYPES_H
#define ESTOP_TYPES_H

#include <cstdint>
#include <string_view>

// Статуси стану двоканальної лінії аварійного вимкнення (E-Stop)
enum class EStopState {
    Normal,        // Обидва NC-контакти замкнені (нормальна робота обладнання)
    Tripped,       // Кнопку натиснуто: обидва NC-контакти розімкнені (аварійна зупинка)
    DiscrepancyError // Розсинхронізація каналів T1/T2 понад допустиме часове вікно (апаратна несправність)
};

// Типи системних подій для логування в журнал ПЛК
enum class LogLevel {
    Info,
    Warning,
    Critical
};

// Структура конфігурації часових параметрів моніторингу E-Stop
struct EStopConfig {
    uint32_t debounce_ms{20};          // Час програмного пригнічення брязкоту контактів (мс)
    uint32_t max_discrepancy_ms{200};  // Максимально допустиме розходження між спрацьовуванням каналів 1 та 2 (мс)
};

#endif // ESTOP_TYPES_H
