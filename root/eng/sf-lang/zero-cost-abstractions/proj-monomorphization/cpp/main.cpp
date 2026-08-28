#include <cstdint>

// Спрощена модель регістрів GPIO (як у CMSIS-заголовку МК)
struct GpioRegs {
    volatile uint32_t MODER;       // +0
    volatile uint32_t reserved[5]; // +4 … +20 (пропуск інших регістрів)
    volatile uint32_t BSRR;        // +24  set/reset — регістр лише для запису
};
#define GPIOA (reinterpret_cast<GpioRegs*>(0x48000000u))

template <uint8_t PIN>
struct Pin {
    static void high() { GPIOA->BSRR = (1u << PIN); }
    static void low()  { GPIOA->BSRR = (1u << (PIN + 16)); }
};

void turn_on() {
    Pin<5>::high();     // читабельно: «ніжка п'ять — увімкнути»
}
