// gpio_profiling.hpp - Атомарне стробування на C++20 з RAII-структурою
#pragma once

#include <cstdint>

namespace Hardware {

class GpioProfiler {
public:
    static inline volatile uint32_t& bsrr() noexcept {
        return *reinterpret_cast<volatile uint32_t*>(0x40020418U);
    }

    static inline void set_high(uint16_t pin_mask) noexcept {
        bsrr() = static_cast<uint32_t>(pin_mask);
    }

    static inline void set_low(uint16_t pin_mask) noexcept {
        bsrr() = (static_cast<uint32_t>(pin_mask) << 16);
    }

    // RAII-клас: піднімає пін при вході в область і опускає при виході
    class ScopedPin {
    public:
        explicit ScopedPin(uint16_t pin_mask) noexcept : mask_(pin_mask) {
            GpioProfiler::set_high(mask_);
        }
        ~ScopedPin() noexcept {
            GpioProfiler::set_low(mask_);
        }
        ScopedPin(const ScopedPin&) = delete;
        ScopedPin& operator=(const ScopedPin&) = delete;
    private:
        uint16_t mask_;
    };
};

} // namespace Hardware
