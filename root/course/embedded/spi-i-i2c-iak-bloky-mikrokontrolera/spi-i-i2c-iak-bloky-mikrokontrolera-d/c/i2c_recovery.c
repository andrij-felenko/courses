#include "i2c_recovery.h"

#include <stdbool.h>

#include "mcu_regs.h"

#define SCL_PIN 6U
#define SDA_PIN 7U

/* Половина періоду 100 кГц. Беремо з запасом: поспішати тут нікуди,
   а повільніший такт розуміє будь-який ведений. */
#define HALF_PERIOD_US 5U

static void pin_as_output_od(unsigned pin)
{
    GPIOB->OTYPER  |=  (1U << pin);            /* відкритий стік */
    GPIOB->PUPDR   &= ~(3U << (pin * 2U));
    GPIOB->PUPDR   |=  (1U << (pin * 2U));
    GPIOB->MODER   &= ~(3U << (pin * 2U));
    GPIOB->MODER   |=  (1U << (pin * 2U));     /* вихід загального призначення */
    GPIOB->OSPEEDR |=  (3U << (pin * 2U));
}

static void pin_as_input_pu(unsigned pin)
{
    GPIOB->PUPDR &= ~(3U << (pin * 2U));
    GPIOB->PUPDR |=  (1U << (pin * 2U));
    GPIOB->MODER &= ~(3U << (pin * 2U));       /* вхід */
}

static void pin_as_i2c(unsigned pin)
{
    GPIOB->OTYPER |= (1U << pin);
    GPIOB->AFR[0] &= ~(0xFU << (pin * 4U));
    GPIOB->AFR[0] |=  (4U << (pin * 4U));      /* AF4 = I2C1 */
    GPIOB->MODER  &= ~(3U << (pin * 2U));
    GPIOB->MODER  |=  (2U << (pin * 2U));      /* альтернативна функція */
}

static void write_pin(unsigned pin, bool level)
{
    /* Вихід із відкритим стоком: "1" означає відпустити лінію, а рівень
       підніме зовнішній резистор. */
    GPIOB->BSRR = level ? (1U << pin) : (1U << (pin + 16U));
}

static bool read_sda(void)
{
    return (GPIOB->IDR & (1U << SDA_PIN)) != 0U;
}

i2c_recovery_t i2c1_bus_recover(void)
{
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOBEN;
    RCC->APB1ENR |= RCC_APB1ENR_I2C1EN;

    /* 1. Блок I2C вимикаємо: поки PE=1, ніжки належать периферії */
    I2C1->CR1 &= ~I2C_CR1_PE;

    /* 2. Забираємо виводи під ручне керування */
    pin_as_output_od(SCL_PIN);
    pin_as_input_pu(SDA_PIN);
    write_pin(SCL_PIN, true);
    delay_us(HALF_PERIOD_US * 2U);

    i2c_recovery_t result = I2C_BUS_FREE;

    if (!read_sda()) {
        /* 3. Ведений тримає SDA у нулі: він завис усередині свого байта.
           Досилаємо йому такти, поки не викладе решту бітів і не відпустить
           лінію в очікуванні ACK. Дев'ять — бо байт плюс такт підтвердження. */
        result = I2C_BUS_STUCK;
        for (int i = 0; i < 9; ++i) {
            write_pin(SCL_PIN, false);
            delay_us(HALF_PERIOD_US);
            write_pin(SCL_PIN, true);
            delay_us(HALF_PERIOD_US);
            if (read_sda()) {
                result = I2C_BUS_RELEASED;
                break;
            }
        }
    }

    if (result != I2C_BUS_STUCK) {
        /* 4. Ручний STOP: перепад SDA з 0 в 1 при високій SCL. Він повертає
           автомати всіх ведених на шині у стан спокою. */
        pin_as_output_od(SDA_PIN);
        write_pin(SCL_PIN, false);
        write_pin(SDA_PIN, false);
        delay_us(HALF_PERIOD_US);
        write_pin(SCL_PIN, true);
        delay_us(HALF_PERIOD_US);
        write_pin(SDA_PIN, true);
        delay_us(HALF_PERIOD_US);
    }

    /* 5. Виводи назад периферії, а сам блок скидаємо: SWRST не лікує
       зовнішній чіп, зате знімає засувку BUSY, яку блок устиг защіпнути,
       побачивши SDA=0 при високій SCL. */
    pin_as_i2c(SCL_PIN);
    pin_as_i2c(SDA_PIN);
    I2C1->CR1 = I2C_CR1_SWRST;
    delay_us(2U);
    I2C1->CR1 = 0U;

    return result;
}
