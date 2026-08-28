// Type-Safe GPIO Strobe на C++20 з використанням RAII
#pragma once
#include <cstdint>

namespace embedded::profiler {

template <uintptr_t PortBase, uint8_t PinIndex>
struct FastGpioPin {
    static_assert(PinIndex < 16, "Pin index must be between 0 and 15");

    static inline void set_high() noexcept {
        auto* bsrr = reinterpret_cast<volatile uint32_t*>(PortBase + 0x18); // Зсув BSRR у STM32
        *bsrr = (1UL << PinIndex);
    }

    static inline void set_low() noexcept {
        auto* bsrr = reinterpret_cast<volatile uint32_t*>(PortBase + 0x18);
        *bsrr = (1UL << (PinIndex + 16));
    }
};

template <typename GpioPinType>
class [[nodiscard]] ScopedGpioStrobe {
public:
    ScopedGpioStrobe() noexcept {
        GpioPinType::set_high();
    }
    ~ScopedGpioStrobe() noexcept {
        GpioPinType::set_low();
    }

    ScopedGpioStrobe(const ScopedGpioStrobe&) = delete;
    ScopedGpioStrobe& operator=(const ScopedGpioStrobe&) = delete;
};

} // namespace embedded::profiler
