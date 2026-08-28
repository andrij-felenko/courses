// Реалізація низькорівневого HAL для STM32 мовою C
#include "stm32f4xx.h"

void stm32_scl_low(void) {
    GPIOB->BSRR = GPIO_BSRR_BR8; // Скидання PB8 в 0
}

void stm32_scl_high_z(void) {
    GPIOB->BSRR = GPIO_BSRR_BS8; // Відпускання PB8 у Hi-Z
}

bool stm32_read_scl(void) {
    return (GPIOB->IDR & GPIO_IDR_ID8) != 0;
}

void stm32_sda_low(void) {
    GPIOB->BSRR = GPIO_BSRR_BR9; // Скидання PB9 в 0
}

void stm32_sda_high_z(void) {
    GPIOB->BSRR = GPIO_BSRR_BS9; // Відпускання PB9 у Hi-Z
}

bool stm32_read_sda(void) {
    return (GPIOB->IDR & GPIO_IDR_ID9) != 0;
}

void stm32_delay_half(void) {
    // Затримка 5 мкс для швидкості 100 кГц (T_SCL/2)
    for (volatile uint32_t i = 0; i < 80; i++) {
        __NOP();
    }
}
