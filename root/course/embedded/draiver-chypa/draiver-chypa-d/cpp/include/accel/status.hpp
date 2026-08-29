// status.hpp — коди помилок і тип результату.
//
// Замість -1 та errno драйвер віддає std::expected: значення або причина, і
// компілятор не дасть скористатися значенням, не перевіривши причини.
#pragma once

#include <cstdint>
#include <expected>
#include <string_view>

namespace accel {

enum class Status : std::int8_t {
    InvalidParam,  // нульовий діапазон, поле не влазить, порожній буфер
    CommFail,      // NACK, шина зайнята, обрив лінії
    Timeout,       // вичерпано квантований ліміт очікування
    NotFound,      // WHO_AM_I не той
    NotInitialised,// робота з чипом до успішної ініціалізації
    NoData         // нового відліку ще немає
};

// Result<void> — операція без значення, але з можливою причиною відмови.
template <typename T>
using Result = std::expected<T, Status>;

[[nodiscard]] constexpr std::string_view describe(Status status) noexcept
{
    switch (status) {
    case Status::InvalidParam:   return "невірний параметр";
    case Status::CommFail:       return "помилка шини";
    case Status::Timeout:        return "тайм-аут очікування";
    case Status::NotFound:       return "чип не відповідає своїм ID";
    case Status::NotInitialised: return "драйвер не ініціалізовано";
    case Status::NoData:         return "нових даних немає";
    }
    return "невідомий код";
}

} // namespace accel
