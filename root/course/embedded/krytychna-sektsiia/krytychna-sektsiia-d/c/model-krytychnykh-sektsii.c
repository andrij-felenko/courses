#include "cmsis_compiler.h"
#include <stdint.h>

#define MAX_SYSCALL_PRIORITY_VALUE (0x50U) // Пріоритет 5 для 4-бітного NVIC

void rtos_aware_critical_section(void) {
    /* 1. Зчитуємо поточний поріг BASEPRI */
    uint32_t saved_basepri = __get_BASEPRI();
    
    /* 
     * 2. Встановлюємо новий поріг через BASEPRI_MAX.
     * __set_BASEPRI_MAX записує нове значення лише у випадку, якщо воно
     * встановлює суворіше маскування, ніж поточне.
     */
    __set_BASEPRI_MAX(MAX_SYSCALL_PRIORITY_VALUE);
    __asm volatile("" ::: "memory");
    
    /* --- Безпечна робота зі структурами драйвера або RTOS --- */
    update_rtos_shared_queue();
    
    __asm volatile("" ::: "memory");
    /* 3. Відновлюємо попереднє значення BASEPRI */
    __set_BASEPRI(saved_basepri);
}
