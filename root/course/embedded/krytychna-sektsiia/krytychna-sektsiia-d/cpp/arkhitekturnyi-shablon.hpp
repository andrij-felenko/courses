#include <cstdint>
#include "cmsis_compiler.h"

void safe_critical_section() noexcept {
    // 1. Зберігаємо поточний стан регістра PRIMASK
    const std::uint32_t saved_primask = __get_PRIMASK();
    
    // 2. Вимикаємо переривання
    __disable_irq();
    
    // 3. Бар'єр пам'яті для компілятора
    __asm volatile("" ::: "memory");
    
    // --- Тіло критичної секції ---
    g_shared_buffer[g_head++] = 0xAA;
    
    // 4. Бар'єр пам'яті перед відновленням
    __asm volatile("" ::: "memory");
    
    // 5. Відновлюємо попередній стан маски
    __set_PRIMASK(saved_primask);
}
