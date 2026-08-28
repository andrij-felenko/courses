#include "critical_section.h"
#include <stdint.h>

/* Апаратний регістр спінлока (приклад для RP2040 SIO_SPINLOCK) */
#define SIO_SPINLOCK0 ((volatile uint32_t*)0xD0000100UL)

void dual_core_critical_section(void) {
    /* 1. Блокуємо локальні переривання ядра */
    critical_section_t cs = critical_section_enter();
    
    /* 2. Захоплюємо апаратний між'ядерний спінлок */
    while (*SIO_SPINLOCK0 == 0U) {
        /* Чекаємо звільнення ресурсу другим ядром */
    }
    
    /* --- Безпечна робота зі спільним ОЗП між двома процесорами --- */
    g_shared_intercore_buffer[0] = 0xFF;
    
    /* 3. Звільняємо між'ядерний спінлок (запис будь-якого значення) */
    *SIO_SPINLOCK0 = 1U;
    
    /* 4. Відновлюємо локальні переривання */
    critical_section_exit(cs);
}
