#include <cstdint>

inline volatile uint32_t& GPIOA_BSRR_REF = *reinterpret_cast<volatile uint32_t*>(0x40010810UL);

void led_on_atomic() noexcept {
    // Атомарне увімкнення без ризику спотворення стану інших виводів
    GPIOA_BSRR_REF = (1U << 5);
}

void led_off_atomic() noexcept {
    // Атомарне вимкнення
    GPIOA_BSRR_REF = (1U << (5 + 16));
}
