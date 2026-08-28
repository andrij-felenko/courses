#include <cstdint>

namespace hardware {

struct GpioPort {
    volatile uint32_t moder;
    volatile uint32_t otyper;
    volatile uint32_t ospeedr;
    volatile uint32_t pupdr;
    volatile uint32_t idr;
    volatile uint32_t odr;
    volatile uint32_t bsrr;
};

inline auto& gpioa = *reinterpret_cast<GpioPort*>(0x40020000UL);

void toggle_pin_odr() {
    gpioa.odr |= (1UL << 5);
}

void set_pin_bsrr() {
    gpioa.bsrr = (1UL << 5);
}

} // namespace hardware
