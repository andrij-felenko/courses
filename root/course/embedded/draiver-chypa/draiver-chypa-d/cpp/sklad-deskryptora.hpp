// C++20: Інкапсуляція стану всередині екземпляра класу
#pragma once
#include <cstdint>

namespace embedded::drivers {

struct DeviceConfig {
    std::uint8_t range{0};
    float scale_factor{1.0F};
    std::uint8_t shadow_ctrl1{0};
    std::uint8_t shadow_ctrl4{0};
    bool is_initialized{false};
};

} // namespace embedded::drivers
