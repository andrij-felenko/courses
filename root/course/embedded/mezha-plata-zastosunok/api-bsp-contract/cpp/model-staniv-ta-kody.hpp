#ifndef BSP_STATUS_HPP
#define BSP_STATUS_HPP

#include <cstdint>
#include <string_view>

namespace bsp {

/**
 * @brief Сильно типізований перелік статусів помилок BSP.
 */
enum class Status : int32_t {
    Ok               =  0,
    InvalidParam     = -1,
    NotInitialized   = -2,
    Busy             = -3,
    Timeout          = -4,
    BusFault         = -5,
    PowerFault       = -6,
    Unsupported      = -7
};

[[nodiscard]] constexpr std::string_view status_to_string(Status s) noexcept {
    switch (s) {
        case Status::Ok:             return "OK";
        case Status::InvalidParam:   return "Invalid parameter";
        case Status::NotInitialized: return "Subsystem not initialized";
        case Status::Busy:           return "Hardware bus busy";
        case Status::Timeout:        return "Hardware timeout";
        case Status::BusFault:       return "Bus transaction fault";
        case Status::PowerFault:     return "Power rail fault";
        case Status::Unsupported:    return "Operation unsupported";
    }
    return "Unknown status";
}

} // namespace bsp

#endif /* BSP_STATUS_HPP */
