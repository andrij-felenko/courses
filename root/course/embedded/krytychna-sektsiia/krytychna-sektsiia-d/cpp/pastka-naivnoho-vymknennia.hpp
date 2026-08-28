#include <cstdint>

extern "C" {
    void __disable_irq(void);
    void __enable_irq(void);
}

// Наївна реалізація критичної секції
void update_system_state(std::uint32_t flags) noexcept {
    __disable_irq(); // Вимикаємо всі переривання
    g_system_flags |= flags;
    __enable_irq();  // Вмикаємо переривання назад
}
