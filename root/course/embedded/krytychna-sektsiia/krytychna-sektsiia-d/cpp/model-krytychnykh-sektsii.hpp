#include "cmsis_compiler.h"
#include <cstdint>

constexpr std::uint32_t kMaxSyscallPriority{0x50U}; // Пріоритет 5 для 4-бітного NVIC

void rtos_aware_critical_section() noexcept {
    // 1. Зчитуємо поточний поріг BASEPRI
    const std::uint32_t saved_basepri = __get_BASEPRI();
    
    // 2. Встановлюємо новий поріг
    __set_BASEPRI_MAX(kMaxSyscallPriority);
    __asm volatile("" ::: "memory");
    
    // --- Безпечна робота зі структурами драйвера або RTOS ---
    update_rtos_shared_queue();
    
    __asm volatile("" ::: "memory");
    // 3. Відновлюємо попереднє значення BASEPRI
    __set_BASEPRI(saved_basepri);
}
