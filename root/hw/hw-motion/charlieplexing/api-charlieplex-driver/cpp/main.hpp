#pragma once
#include <cstdint>
#include <span>
#include <array>
#include <optional>

namespace charlieplex {

enum class PinState : uint8_t {
    HiZ  = 0,
    High = 1,
    Low  = 2
};

enum class Status : int8_t {
    Ok             =  0,
    InvalidArg     = -1,
    OutOfBound     = -2,
    Uninitialized  = -3
};

struct LedMapping {
    uint8_t anode;
    uint8_t cathode;
};

template <size_t Pins>
struct MatrixTraits {
    static constexpr size_t PinCount = Pins;
    static constexpr size_t LedCount = Pins * (Pins - 1);
};

struct DriverHal {
    void (*setPinState)(uint8_t pinIndex, PinState state);
    void (*enterCritical)();
    void (*exitCritical)();
};

} // namespace charlieplex
