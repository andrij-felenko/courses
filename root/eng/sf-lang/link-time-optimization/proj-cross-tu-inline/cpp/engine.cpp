// engine.cpp — реалізація логіки та обробки (C++)
#include "engine.hpp"

std::int32_t GainFilter::process(std::int32_t sample) const noexcept {
    return sample * gain_;
}

std::int32_t fast_scale(std::int32_t value, std::int32_t factor) noexcept {
    return (value * factor) + 7;
}

std::int32_t dead_helper_function(std::int32_t x) noexcept {
    return (x ^ 0x55AA55AA) + 12345;
}
