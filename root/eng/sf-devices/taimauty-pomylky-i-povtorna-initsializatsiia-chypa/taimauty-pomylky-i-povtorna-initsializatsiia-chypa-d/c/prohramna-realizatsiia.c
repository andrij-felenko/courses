#include <stdint.h>
#include <stdbool.h>
#include "stm32f4xx.h"

static void delay_dwt_us(uint32_t us) {
    uint32_t start = DWT->CYCCNT;
    uint32_t ticks = (uint32_t)(((uint64_t)us * SystemCoreClock) / 1000000ULL);
    while ((uint32_t)(DWT->CYCCNT - start) < ticks);
}

int i2c_bus_recover_9_pulses(GPIO_TypeDef *scl_port, uint16_t scl_pin,
                             GPIO_TypeDef *sda_port, uint16_t sda_pin,
                             I2C_TypeDef *i2c) {
    // 1. Вимикаємо периферійний модуль I2C
    i2c->CR1 &= ~I2C_CR1_PE;

    // 2. Налаштовуємо виводи SCL та SDA як GPIO Open-Drain Output
    scl_port->BSRR = (1U << scl_pin);
    sda_port->BSRR = (1U << sda_pin);

    // SCL -> Output Open-Drain
    scl_port->MODER &= ~(3U << (scl_pin * 2));
    scl_port->MODER |= (1U << (scl_pin * 2));
    scl_port->OTYPER |= (1U << scl_pin);
    scl_port->OSPEEDR |= (3U << (scl_pin * 2)); // High speed

    // SDA -> Output Open-Drain
    sda_port->MODER &= ~(3U << (sda_pin * 2));
    sda_port->MODER |= (1U << (sda_pin * 2));
    sda_port->OTYPER |= (1U << sda_pin);
    sda_port->OSPEEDR |= (3U << (sda_pin * 2));

    delay_dwt_us(10);

    // 3. Перевіряємо, чи не затиснута лінія SCL веденим чипом
    if ((scl_port->IDR & (1U << scl_pin)) == 0) {
        return -2; // SCL stuck low: Clock stretching failure
    }

    // 4. Генеруємо до 9 тактових імпульсів на SCL
    bool sda_freed = false;
    for (int i = 0; i < 9; i++) {
        // Якщо SDA вже відпущено веденим, виходимо
        if ((sda_port->IDR & (1U << sda_pin)) != 0) {
            sda_freed = true;
            break;
        }

        // SCL = 0 (Low)
        scl_port->BSRR = (1U << (scl_pin + 16));
        delay_dwt_us(5); // t_LOW >= 4.7 us

        // SCL = 1 (High)
        scl_port->BSRR = (1U << scl_pin);
        delay_dwt_us(5); // t_HIGH >= 4.0 us
    }

    if ((sda_port->IDR & (1U << sda_pin)) != 0) {
        sda_freed = true;
    }

    // 5. Формуємо примусову умову STOP: SDA 0 -> 1 при SCL = 1
    sda_port->BSRR = (1U << (sda_pin + 16)); // SDA = 0
    delay_dwt_us(5);
    scl_port->BSRR = (1U << scl_pin);        // SCL = 1
    delay_dwt_us(5);
    sda_port->BSRR = (1U << sda_pin);        // SDA = 1 (STOP фронт)
    delay_dwt_us(10);

    // 6. Повертаємо виводи в режим альтернативної функції I2C (AF4)
    scl_port->MODER &= ~(3U << (scl_pin * 2));
    scl_port->MODER |= (2U << (scl_pin * 2)); // AF mode
    sda_port->MODER &= ~(3U << (sda_pin * 2));
    sda_port->MODER |= (2U << (sda_pin * 2)); // AF mode

    // 7. Скидаємо та переініціалізуємо апаратний модуль I2C
    i2c->CR1 |= I2C_CR1_SWRST;
    delay_dwt_us(5);
    i2c->CR1 &= ~I2C_CR1_SWRST;
    i2c->CR1 |= I2C_CR1_PE;

    return sda_freed ? 0 : -1;
}
