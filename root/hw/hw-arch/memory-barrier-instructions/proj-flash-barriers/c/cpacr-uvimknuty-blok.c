#include <stdint.h>

#define CPACR (*(volatile uint32_t *)0xE000ED88u)  // Coprocessor Access Control

static inline void dsb(void) { __asm volatile ("dsb 0xF" ::: "memory"); }
static inline void isb(void) { __asm volatile ("isb 0xF" ::: "memory"); }

void enable_fpu(void)
{
    CPACR |= (0xFu << 20);  // повний доступ до CP10 і CP11 (біти 20…23)
    dsb();                  // дочекатися, поки запис у CPACR завершиться
    isb();                  // перечитати наступні команди вже з увімкненим FPU
    // лише ТУТ безпечно виконувати команди з рухомою комою
}
