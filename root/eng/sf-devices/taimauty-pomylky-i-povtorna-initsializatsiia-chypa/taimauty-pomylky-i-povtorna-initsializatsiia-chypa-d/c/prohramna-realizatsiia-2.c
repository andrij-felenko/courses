#include <stdint.h>
#include <stdbool.h>
#include "stm32f4xx.h"

typedef struct {
    GPIO_TypeDef *pwr_port;
    uint16_t pwr_pin;       // 1 = Power ON (MOSFET відкритий), 0 = Power OFF
    GPIO_TypeDef *nrst_port;
    uint16_t nrst_pin;
    GPIO_TypeDef *scl_port;
    uint16_t scl_pin;
    GPIO_TypeDef *sda_port;
    uint16_t sda_pin;
} chip_hardware_bus_t;

static void delay_ms_dwt(uint32_t ms) {
    for (uint32_t i = 0; i < ms; i++) {
        uint32_t start = DWT->CYCCNT;
        uint32_t ticks = SystemCoreClock / 1000U;
        while ((uint32_t)(DWT->CYCCNT - start) < ticks);
    }
}

void chip_execute_power_cycle(const chip_hardware_bus_t *hw) {
    // 1. Повна ізоляція шини: переводимо SCL, SDA та nRESET у режим Analog Hi-Z
    hw->scl_port->MODER |= (3U << (hw->scl_pin * 2));
    hw->scl_port->PUPDR &= ~(3U << (hw->scl_pin * 2));

    hw->sda_port->MODER |= (3U << (hw->sda_pin * 2));
    hw->sda_port->PUPDR &= ~(3U << (hw->sda_pin * 2));

    if (hw->nrst_port) {
        hw->nrst_port->MODER |= (3U << (hw->nrst_pin * 2));
        hw->nrst_port->PUPDR &= ~(3U << (hw->nrst_pin * 2));
    }

    // 2. Вимикаємо живлення (MOSFET OFF)
    hw->pwr_port->BSRR = (1U << (hw->pwr_pin + 16));

    // 3. Чекаємо гарантованого розряду блокувальних конденсаторів (50 мс)
    delay_ms_dwt(50);

    // 4. Подаємо живлення (MOSFET ON)
    hw->pwr_port->BSRR = (1U << hw->pwr_pin);

    // 5. Очікуємо стабілізації напруги та завершення POR чипа (20 мс)
    delay_ms_dwt(20);

    // 6. Відновлюємо вивід nRESET у робочий стан HIGH
    if (hw->nrst_port) {
        hw->nrst_port->MODER &= ~(3U << (hw->nrst_pin * 2));
        hw->nrst_port->MODER |= (1U << (hw->nrst_pin * 2)); // Output mode
        hw->nrst_port->BSRR = (1U << hw->nrst_pin);         // High
    }
}
