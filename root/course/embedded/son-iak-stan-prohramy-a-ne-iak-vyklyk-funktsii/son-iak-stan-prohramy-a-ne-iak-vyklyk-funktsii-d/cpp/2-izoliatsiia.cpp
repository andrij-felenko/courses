/* Переведення невикористовуваних пінів порту GPIOA в аналоговий режим (C++20) */
#include <cstdint>

namespace emb::hw {

struct GpioPort {
    volatile uint32_t MODER;
    volatile uint32_t OTYPER;
    volatile uint32_t OSPEEDR;
    volatile uint32_t PUPDR;
};

inline void isolateUnusedPins(GpioPort* port) noexcept {
    if (port != nullptr) {
        port->MODER = 0xFFFFFFFFU; // Analog Mode
        port->PUPDR = 0x00000000U; // No pull
    }
}

} // namespace emb::hw
