#include <stdint.h>

#define SCB_VTOR_REG (*(volatile uint32_t*)0xE000ED08)

extern uint32_t _isr_vector_start;

void relocate_vector_table_c(void) {
    /* Вимкнення глобальних переривань */
    __builtin_arm_set_primask(1);

    /* Запис базової адреси нової таблиці векторів */
    SCB_VTOR_REG = (uint32_t)&_isr_vector_start;

    /* Бар'єри пам'яті для синхронізації процесорного конвеєра */
    __builtin_arm_dsb(15);
    __builtin_arm_isb(15);

    /* Увімкнення переривань */
    __builtin_arm_set_primask(0);
}
