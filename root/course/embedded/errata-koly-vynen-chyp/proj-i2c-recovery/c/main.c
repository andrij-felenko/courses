#include "stm32f10x.h"
#include <stdbool.h>
#include <stdint.h>

#define I2C_TIMEOUT_CYCLES  10000U

/* Проста затримка для формування фронтів I2C (близько 5 мкс при 72 МГц) */
static void delay_cycles(volatile uint32_t count) {
    while (count--) {
        __NOP();
    }
}

/**
 * @brief Повне апаратне та програмне відновлення шини I2C1
 * @return true, якщо шина успішно звільнена і модуль ініціалізовано
 */
bool i2c1_bus_recover_and_init(void) {
    /* 1. Примусове апаратне скидання периферії I2C1 через RCC */
    RCC->APB1RSTR |= RCC_APB1RSTR_I2C1RST;
    delay_cycles(100);
    RCC->APB1RSTR &= ~RCC_APB1RSTR_I2C1RST;

    /* 2. Увімкнення тактування портів GPIOB та I2C1 */
    RCC->APB2ENR |= RCC_APB2ENR_IOPBEN;
    RCC->APB1ENR |= RCC_APB1ENR_I2C1EN;

    /* 3. Конфігурація PB6 (SCL) та PB7 (SDA) як GPIO Open-Drain 10 МГц */
    /* Очищення бітів MODE6, CNF6, MODE7, CNF7 (0xF << 24 | 0xF << 28) */
    GPIOB->CRL &= ~(0xFF000000U);
    /* 0x7 = Open-Drain вихід 10 МГц (CNF=01b, MODE=01b) */
    GPIOB->CRL |= (0x77000000U);

    /* Початковий стан: відпускаємо обидві лінії в HIGH */
    GPIOB->BSRR = GPIO_BSRR_BS6 | GPIO_BSRR_BS7;
    delay_cycles(200);

    /* 4. Генерація до 9 тактів SCL, якщо SDA затиснутий зовнішнім слейвом */
    for (uint8_t i = 0; i < 9; ++i) {
        /* Якщо лінія SDA вже відпущена в HIGH — ведений пристрій вільний */
        if (GPIOB->IDR & GPIO_IDR_IDR7) {
            break;
        }

        /* Імпульс на SCL: LOW -> пауза -> HIGH -> пауза */
        GPIOB->BSRR = GPIO_BSRR_BR6;
        delay_cycles(200);
        GPIOB->BSRR = GPIO_BSRR_BS6;
        delay_cycles(200);
    }

    /* 5. Генерація ручного стану STOP: SDA LOW, SCL HIGH -> SDA HIGH */
    GPIOB->BSRR = GPIO_BSRR_BR7; /* SDA = 0 */
    delay_cycles(200);
    GPIOB->BSRR = GPIO_BSRR_BS6; /* SCL = 1 */
    delay_cycles(200);
    GPIOB->BSRR = GPIO_BSRR_BS7; /* SDA = 1 (STOP condition) */
    delay_cycles(200);

    /* Перевірка, чи звільнилася шина (обидві лінії мають бути в 1) */
    if ((GPIOB->IDR & (GPIO_IDR_IDR6 | GPIO_IDR_IDR7)) != (GPIO_IDR_IDR6 | GPIO_IDR_IDR7)) {
        return false; /* Апаратне коротке замикання або несправний чип на платі */
    }

    /* 6. Переведення PB6/PB7 у режим Alternate Function Open-Drain (0xB = CNF=11b, MODE=01b) */
    GPIOB->CRL &= ~(0xFF000000U);
    GPIOB->CRL |= (0xBB000000U);

    /* 7. Ініціалізація регістрів I2C1 на частоту 100 кГц (APB1 = 36 МГц) */
    I2C1->CR1 = I2C_CR1_SWRST; /* Програмне скидання всередині блоку */
    delay_cycles(50);
    I2C1->CR1 = 0;

    I2C1->CR2 = 36;             /* Вхідна частота APB1 = 36 МГц */
    I2C1->CCR = 180;            /* 100 кГц: 36 МГц / (2 * 100 кГц) = 180 */
    I2C1->TRISE = 37;           /* Максимальний час наростання: 36 + 1 */
    I2C1->CR1 |= I2C_CR1_PE;    /* Увімкнення модуля */

    return true;
}
