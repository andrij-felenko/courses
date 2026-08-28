// C++20: Строго типізоване перерахування статусів з std::int32_t
#pragma once
#include <cstdint>

namespace embedded::drivers {

enum class Status : std::int32_t {
    Ok                  =  0,  ///< Успішне виконання
    InvalidParam        = -1,  ///< Некоректні аргументи виклику
    CommFail            = -2,  ///< Фізичний збій лінії зв'язку
    Timeout             = -3,  ///< Перевищено ліміт часу операції
    DeviceNotFound      = -4,  ///< Не знайдено мікросхему з відповідним ID
    NotInitialized      = -5,  ///< Дескриптор не ініціалізовано
    DataNotReady        = -6,  ///< Нові відліки відсутні
    SelfTestFailed      = -7,  ///< Помилка вбудованого тестування
    CalibrationInvalid  = -8   ///< Невалідна таблиця калібрування
};

} // namespace embedded::drivers
