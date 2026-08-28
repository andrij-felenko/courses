#include <stdint.h>
#include "cmsis_compiler.h"

void safe_critical_section(void) {
    /* 1. Зберігаємо поточний стан регістра PRIMASK */
    uint32_t saved_primask = __get_PRIMASK();
    
    /* 2. Вимикаємо переривання (встановлюємо PRIMASK = 1) */
    __disable_irq();
    
    /* 
     * 3. Бар'єр пам'яті для оптимізатора компілятора.
     * Забороняє компілятору виносити інструкції читання/запису за межі блоку.
     */
    __asm volatile("" ::: "memory");
    
    /* --- Тіло критичної секції: безпечна робота зі спільними даними --- */
    g_shared_buffer[g_head++] = 0xAA;
    
    /* 4. Бар'єр пам'яті перед відновленням */
    __asm volatile("" ::: "memory");
    
    /* 5. Відновлюємо саме той стан, який був до входу в функцію */
    __set_PRIMASK(saved_primask);
}
