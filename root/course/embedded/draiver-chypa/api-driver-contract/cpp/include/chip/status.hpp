// Таксономія статусів. Той самий словник, що й у C-контракті, але enum class:
// значення не сплутати з int і не додати випадково до лічильника.
#pragma once

#include <cstdint>
#include <string_view>

namespace chip {

enum class Status : std::int32_t {
    Ok                 =  0,  ///< Операція успішно завершена
    InvalidParam       = -1,  ///< Некоректні аргументи виклику
    CommFail           = -2,  ///< NACK, втрата арбітражу, зависла шина
    Timeout            = -3,  ///< Вичерпано очікування готовності
    DeviceNotFound     = -4,  ///< WHO_AM_I містить неочікуваний ідентифікатор
    NotInitialized     = -5,  ///< Виклик до init()
    DataNotReady       = -6,  ///< Нової вибірки ще немає
    SelfTestFailed     = -7,  ///< Самотест вийшов за паспортне вікно
    CalibrationInvalid = -8   ///< Коефіцієнти підстроювання з NVM не піднялися
};

[[nodiscard]] constexpr std::string_view to_string(Status status) noexcept
{
    switch (status) {
    case Status::Ok:                 return "Ok";
    case Status::InvalidParam:       return "InvalidParam";
    case Status::CommFail:           return "CommFail";
    case Status::Timeout:            return "Timeout";
    case Status::DeviceNotFound:     return "DeviceNotFound";
    case Status::NotInitialized:     return "NotInitialized";
    case Status::DataNotReady:       return "DataNotReady";
    case Status::SelfTestFailed:     return "SelfTestFailed";
    case Status::CalibrationInvalid: return "CalibrationInvalid";
    }
    return "Unknown";
}

} // namespace chip
