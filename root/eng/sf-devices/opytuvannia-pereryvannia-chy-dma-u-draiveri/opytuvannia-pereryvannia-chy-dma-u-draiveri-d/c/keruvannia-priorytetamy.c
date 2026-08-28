#include <stdint.h>

#define DRIVER_MAX_SYSCALL_PRIORITY 0x50 // Маскуємо пріоритети від 5 і нижче

static inline uint32_t Driver_EnterCritical(void) {
    uint32_t prev_basepri;
    __asm volatile (
        "mrs %0, basepri\n"
        "msr basepri, %1\n"
        "isb\n"
        : "=r" (prev_basepri)
        : "r" (DRIVER_MAX_SYSCALL_PRIORITY)
        : "memory"
    );
    return prev_basepri;
}

static inline void Driver_ExitCritical(uint32_t prev_basepri) {
    __asm volatile (
        "msr basepri, %0\n"
        "isb\n"
        :
        : "r" (prev_basepri)
        : "memory"
    );
}
