#include "stm32f10x.h"
#include <stdbool.h>
#include <stdint.h>

#define HW_POLL_TIMEOUT_CYCLES  50000U

typedef enum {
    DRIVER_OK = 0,
    DRIVER_ERR_TIMEOUT,
    DRIVER_ERR_BUS_STUCK
} DriverStatus;

/**
 * @brief Безпечне очікування встановлення прапорця з тайм-аутом
 */
DriverStatus safe_wait_flag(volatile uint32_t *reg, uint32_t mask, bool wait_for_set) {
    uint32_t timeout = HW_POLL_TIMEOUT_CYCLES;

    while (timeout > 0) {
        bool is_set = ((*reg & mask) != 0U);
        if (is_set == wait_for_set) {
            return DRIVER_OK;
        }
        --timeout;
        __NOP();
    }

    return DRIVER_ERR_TIMEOUT;
}

/**
 * @brief Приклад передачі байта з автоматичним відновленням при збої кремнію
 */
DriverStatus i2c_transmit_byte_defensive(I2C_TypeDef *i2c, uint8_t byte) {
    /* 1. Очікування звільнення регістра передавача (TXE) */
    if (safe_wait_flag(&(i2c->SR1), I2C_SR1_TXE, true) != DRIVER_OK) {
        /* Апаратний збій або зависання лінії: запускаємо аварійний скид */
        RCC->APB1RSTR |= RCC_APB1RSTR_I2C1RST;
        __NOP(); __NOP();
        RCC->APB1RSTR &= ~RCC_APB1RSTR_I2C1RST;
        return DRIVER_ERR_TIMEOUT;
    }

    /* 2. Запис даних у регістр */
    i2c->DR = byte;
    return DRIVER_OK;
}
