#ifndef I2C_BUS_RECOVERY_H
#define I2C_BUS_RECOVERY_H

#include <stdint.h>
#include <stdbool.h>
#include "stm32f4xx.h"
#include "dwt_timeout.h"

typedef enum {
    I2C_RECOVER_OK = 0,
    I2C_RECOVER_ERR_SCL_STUCK_LOW = -1,
    I2C_RECOVER_ERR_SDA_STUCK_LOW = -2,
    I2C_RECOVER_ERR_NULL_PARAM = -3
} i2c_recover_status_t;

typedef struct {
    I2C_TypeDef *i2c;
    GPIO_TypeDef *scl_port;
    uint8_t scl_pin;
    GPIO_TypeDef *sda_port;
    uint8_t sda_pin;
    uint8_t scl_af;
    uint8_t sda_af;
} i2c_bus_hardware_t;

static inline void i2c_pin_set_output_od(GPIO_TypeDef *port, uint8_t pin) {
    // Встановлюємо високий рівень перед конфігурацією виходу
    port->BSRR = (1U << pin);
    // Mode = Output (01)
    port->MODER &= ~(3U << (pin * 2));
    port->MODER |= (1U << (pin * 2));
    // Output Type = Open Drain (1)
    port->OTYPER |= (1U << pin);
    // Speed = High Speed (11)
    port->OSPEEDR |= (3U << (pin * 2));
    // No Pull (00)
    port->PUPDR &= ~(3U << (pin * 2));
}

static inline void i2c_pin_set_af_od(GPIO_TypeDef *port, uint8_t pin, uint8_t af) {
    // Mode = Alternate Function (10)
    port->MODER &= ~(3U << (pin * 2));
    port->MODER |= (2U << (pin * 2));
    // Output Type = Open Drain (1)
    port->OTYPER |= (1U << pin);
    // AF selection
    if (pin < 8) {
        port->AFR[0] &= ~(0xFU << (pin * 4));
        port->AFR[0] |= ((uint32_t)af << (pin * 4));
    } else {
        port->AFR[1] &= ~(0xFU << ((pin - 8) * 4));
        port->AFR[1] |= ((uint32_t)af << ((pin - 8) * 4));
    }
}

i2c_recover_status_t i2c_bus_unlock_9_pulses(const i2c_bus_hardware_t *hw, uint8_t *out_pulses_needed) {
    if (!hw || !hw->i2c || !hw->scl_port || !hw->sda_port) {
        return I2C_RECOVER_ERR_NULL_PARAM;
    }

    if (out_pulses_needed) {
        *out_pulses_needed = 0;
    }

    // 1. Вимикаємо апаратний блок I2C
    hw->i2c->CR1 &= ~I2C_CR1_PE;

    // 2. Переводимо SCL та SDA у GPIO Open-Drain
    i2c_pin_set_output_od(hw->scl_port, hw->scl_pin);
    i2c_pin_set_output_od(hw->sda_port, hw->sda_pin);

    dwt_delay_us(10);

    // 3. Перевіряємо лінію SCL на затискання веденим
    if ((hw->scl_port->IDR & (1U << hw->scl_pin)) == 0) {
        // SCL притиснута до землі: фатальний збій Clock Stretching
        i2c_pin_set_af_od(hw->scl_port, hw->scl_pin, hw->scl_af);
        i2c_pin_set_af_od(hw->sda_port, hw->sda_pin, hw->sda_af);
        return I2C_RECOVER_ERR_SCL_STUCK_LOW;
    }

    // 4. Генерація серії до 9 тактових імпульсів
    bool sda_freed = false;
    uint8_t pulse_count = 0;

    for (pulse_count = 0; pulse_count < 9; pulse_count++) {
        // Якщо SDA вже у високому рівні, шину розблоковано
        if ((hw->sda_port->IDR & (1U << hw->sda_pin)) != 0) {
            sda_freed = true;
            break;
        }

        // SCL = 0 (Low)
        hw->scl_port->BSRR = (1U << (hw->scl_pin + 16));
        dwt_delay_us(5); // t_LOW >= 4.7 us

        // SCL = 1 (High)
        hw->scl_port->BSRR = (1U << hw->scl_pin);
        dwt_delay_us(5); // t_HIGH >= 4.0 us
    }

    if ((hw->sda_port->IDR & (1U << hw->sda_pin)) != 0) {
        sda_freed = true;
    }

    if (out_pulses_needed) {
        *out_pulses_needed = pulse_count;
    }

    // 5. Примусова генерація умови STOP: SDA 0 -> 1 при SCL = 1
    hw->sda_port->BSRR = (1U << (hw->sda_pin + 16)); // SDA = 0
    dwt_delay_us(5);
    hw->scl_port->BSRR = (1U << hw->scl_pin);        // SCL = 1
    dwt_delay_us(5);
    hw->sda_port->BSRR = (1U << hw->sda_pin);        // SDA = 1
    dwt_delay_us(10);

    // 6. Повертаємо виводи в режим Alternate Function
    i2c_pin_set_af_od(hw->scl_port, hw->scl_pin, hw->scl_af);
    i2c_pin_set_af_od(hw->sda_port, hw->sda_pin, hw->sda_af);

    // 7. Скидаємо модуль I2C через регістр SWRST
    hw->i2c->CR1 |= I2C_CR1_SWRST;
    dwt_delay_us(5);
    hw->i2c->CR1 &= ~I2C_CR1_SWRST;

    // Вмикаємо периферійний модуль
    hw->i2c->CR1 |= I2C_CR1_PE;

    return sda_freed ? I2C_RECOVER_OK : I2C_RECOVER_ERR_SDA_STUCK_LOW;
}

#endif // I2C_BUS_RECOVERY_H
