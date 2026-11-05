#include "stm32f4xx.h"
#include <stdint.h>
#include <stdbool.h>

#define I2C_TIMEOUT_CYCLES  100000U // Максимальна кількість тактів очікування

// Розміщення функції відновлення шини в ОЗП (RAM function) для усунення затримок флеш-пам'яті
__attribute__((section(".ramfunc"), noinline))
bool bitbang_i2c_recover_bus(GPIO_TypeDef* port_scl, uint16_t pin_scl,
                             GPIO_TypeDef* port_sda, uint16_t pin_sda) {
    
    uint32_t scl_set   = (uint32_t)pin_scl;
    uint32_t scl_reset = (uint32_t)pin_scl << 16;
    uint32_t sda_set   = (uint32_t)pin_sda;
    uint32_t sda_reset = (uint32_t)pin_sda << 16;

    // 1. Перевірка: якщо SDA вже у високому рівні, шина не зависла
    if (port_sda->IDR & pin_sda) {
        return true;
    }

    // 2. Генерація до 9 імпульсів SCL для розблокування веденого пристрою
    for (uint8_t i = 0; i < 9; i++) {
        port_scl->BSRR = scl_reset; // SCL low
        
        // Затримка демпфування
        for (volatile int d = 0; d < 50; d++) { __NOP(); }

        port_scl->BSRR = scl_set;   // SCL high
        
        for (volatile int d = 0; d < 50; d++) { __NOP(); }

        // Перевірка, чи відпустив ведений пристрій лінію SDA
        if (port_sda->IDR & pin_sda) {
            break; // SDA відновлено
        }
    }

    // 3. Формування примусової генерації умови STOP (SDA розмикається при високому SCL)
    port_sda->BSRR = sda_reset; // SDA low
    for (volatile int d = 0; d < 50; d++) { __NOP(); }
    
    port_scl->BSRR = scl_set;   // SCL high
    for (volatile int d = 0; d < 50; d++) { __NOP(); }
    
    port_sda->BSRR = sda_set;   // SDA high (STOP condition)
    for (volatile int d = 0; d < 50; d++) { __NOP(); }

    // Повертаємо true, якщо лінія SDA успішно звільнена
    return (port_sda->IDR & pin_sda) != 0;
}
