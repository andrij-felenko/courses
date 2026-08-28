#include "stm32f4xx.h"
#include <cstdint>

namespace mcu::debug {

/**
 * @brief Клас захисту інтерфейсу налагодження на етапі старту (Zero-overhead guard).
 */
class SafetyBarrier {
public:
    static void apply_boot_guard(uint32_t loop_count = 2'000'000U) noexcept {
        // Дозволяємо тактування порту користувацької кнопки для екстреного входу в цикл
        RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
        GPIOA->MODER &= ~(0x3U << (0 * 2)); // Вхід PA0

        // Якщо кнопка утримується під час подачі живлення — блокуємо перехід у сон
        if ((GPIOA->IDR & (1U << 0)) != 0) {
            while (true) {
                asm volatile("nop");
            }
        }

        // Програмний інтервал затримки для підключення OpenOCD/ST-Link
        for (volatile uint32_t i = 0; i < loop_count; ++i) {
            asm volatile("nop");
        }
    }
};

} // namespace mcu::debug

int main() {
    // Захисний бар'єр гарантує збереження доступу до ядра під час розробки
    mcu::debug::SafetyBarrier::apply_boot_guard();

    // Робоча ініціалізація периферії
    
    while (true) {
    }
}
