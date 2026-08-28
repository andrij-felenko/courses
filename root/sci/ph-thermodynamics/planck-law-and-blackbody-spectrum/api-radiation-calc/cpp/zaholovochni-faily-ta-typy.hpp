#ifndef BLACKBODY_HPP
#define BLACKBODY_HPP

#include <cstddef>
#include <expected>
#include <span>
#include <string_view>

namespace blackbody {

/* Статуси виконання обчислювальних операцій C++20 */
enum class Status {
    Success = 0,
    InvalidTemperature = -1,
    InvalidWavelength = -2,
    InvalidRange = -3,
    Overflow = -4,
    IntegrationFailed = -5
};

} // namespace blackbody

#endif // BLACKBODY_HPP
