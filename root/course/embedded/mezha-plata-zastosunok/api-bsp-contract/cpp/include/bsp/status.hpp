#pragma once

#include <cstdint>
#include <expected>
#include <string_view>

namespace bsp {

/**
 * @brief Сильно типізований перелік статусів помилок BSP.
 */
enum class Status : std::int32_t {
    Ok             =  0,
    InvalidParam   = -1,
    NotInitialized = -2,
    Busy           = -3,
    Timeout        = -4,
    BusFault       = -5,
    PowerFault     = -6,
    Unsupported    = -7
};

/**
 * @brief Результат операції без корисного значення.
 *
 * Помилку неможливо мовчки проігнорувати: std::expected позначено
 * [[nodiscard]] у самій бібліотеці, а Status не перетворюється на int.
 */
using Result = std::expected<void, Status>;

/** Скорочення для повернення помилки: `return fail(Status::Busy);` */
[[nodiscard]] constexpr std::unexpected<Status> fail(Status s) noexcept {
    return std::unexpected{s};
}

[[nodiscard]] constexpr std::string_view status_to_string(Status s) noexcept {
    switch (s) {
        case Status::Ok:             return "OK";
        case Status::InvalidParam:   return "invalid parameter";
        case Status::NotInitialized: return "subsystem not initialized";
        case Status::Busy:           return "hardware bus busy";
        case Status::Timeout:        return "hardware timeout";
        case Status::BusFault:       return "bus transaction fault";
        case Status::PowerFault:     return "power rail fault";
        case Status::Unsupported:    return "operation unsupported";
    }
    return "unknown status";
}

} // namespace bsp
