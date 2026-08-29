// status.hpp — таксономія відмов драйвера.
//
// Код повернення тут не число, а тип: std::expected змушує викликача або
// подивитися в помилку, або явно її проігнорувати. Забути перевірку, як це
// стається з int-кодами, компілятор не дає — [[nodiscard]] на місці.
#pragma once

#include <string_view>

namespace chip {

enum class Error {
    InvalidParam,   // аргумент поза межами дозволеного
    Comm,           // апаратна помилка шини: NACK, обрив, зайнято
    DeviceNotFound, // WHO_AM_I не збігся з очікуваним ідентифікатором
    NotInitialized, // звернення до пристрою до успішної ініціалізації
    NoData          // нового відліку ще немає (DRDY = 0)
};

[[nodiscard]] constexpr std::string_view toString(Error error) noexcept
{
    switch (error) {
    case Error::InvalidParam:   return "INVALID_PARAM";
    case Error::Comm:           return "COMM";
    case Error::DeviceNotFound: return "DEVICE_NOT_FOUND";
    case Error::NotInitialized: return "NOT_INITIALIZED";
    case Error::NoData:         return "NO_DATA";
    }
    return "UNKNOWN";
}

} // namespace chip
