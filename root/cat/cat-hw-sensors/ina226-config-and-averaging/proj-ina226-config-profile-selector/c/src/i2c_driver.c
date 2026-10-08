/**
 * @file i2c_driver.c
 * @brief Низькорівнева реалізація обміну I2C для STM32 через прямий доступ до регістрів.
 *
 * Опитування прапорців SR1/SR2, генерація послідовностей START/STOP, перетворення big-endian в little-endian.
 */

#include "i2c_driver.h"

/* Структура регістрів периферичного модуля STM32 I2C */
typedef struct {
    volatile uint32_t CR1;   /**< Control Register 1 */
    volatile uint32_t CR2;   /**< Control Register 2 */
    volatile uint32_t OAR1;  /**< Own Address Register 1 */
    volatile uint32_t OAR2;  /**< Own Address Register 2 */
    volatile uint32_t DR;    /**< Data Register */
    volatile uint32_t SR1;   /**< Status Register 1 */
    volatile uint32_t SR2;   /**< Status Register 2 */
    volatile uint32_t CCR;   /**< Clock Control Register */
    volatile uint32_t TRISE; /**< TRISE Register */
} STM32_I2C_TypeDef;

#define STM32_I2C1_BASE       0x40005400U
#define I2C1_PERIPH           ((STM32_I2C_TypeDef *)STM32_I2C1_BASE)

/* Бітові маски сигнальних прапорців STM32 I2C */
#define I2C_CR1_PE            (1U << 0)
#define I2C_CR1_START         (1U << 8)
#define I2C_CR1_STOP          (1U << 9)
#define I2C_CR1_ACK           (1U << 10)
#define I2C_CR1_SWRST         (1U << 15)

#define I2C_SR1_SB            (1U << 0)   /**< Start Bit Generated */
#define I2C_SR1_ADDR          (1U << 1)   /**< Address Sent/Matched */
#define I2C_SR1_BTF           (1U << 2)   /**< Byte Transfer Finished */
#define I2C_SR1_RXNE          (1U << 6)   /**< Data Register Not Empty (RX) */
#define I2C_SR1_TXE           (1U << 7)   /**< Data Register Empty (TX) */
#define I2C_SR1_AF            (1U << 10)  /**< Acknowledge Failure */

#define I2C_SR2_BUSY          (1U << 1)   /**< Bus Busy Flag */

#define I2C_TIMEOUT_CYCLES    50000U

/**
 * @brief Допоміжна неблокуюча функція очікування біта в регістрі з таймаутом.
 */
static i2c_status_t wait_flag(volatile uint32_t *reg, uint32_t flag, bool set)
{
    uint32_t timeout = I2C_TIMEOUT_CYCLES;
    while (timeout--) {
        bool current = ((*reg & flag) != 0U);
        if (current == set) {
            return I2C_OK;
        }
    }
    return I2C_ERR_TIMEOUT;
}

/**
 * @brief Ініціалізація периферії I2C1.
 */
i2c_status_t i2c1_init(uint32_t clock_speed_hz)
{
    (void)clock_speed_hz;
    
    /* Програмний скид модуля I2C1 */
    I2C1_PERIPH->CR1 |= I2C_CR1_SWRST;
    I2C1_PERIPH->CR1 &= ~I2C_CR1_SWRST;

    /* Налаштування тактування (припускаємо PCLK1 = 36 МГц) */
    I2C1_PERIPH->CR2 = 36U;          /* FREQ[5:0] = 36 */
    I2C1_PERIPH->CCR = 180U;         /* 100 кГц Standard mode */
    I2C1_PERIPH->TRISE = 37U;        /* Max rise time */

    /* Увімкнення периферії I2C1 */
    I2C1_PERIPH->CR1 |= I2C_CR1_PE;

    return I2C_OK;
}

/**
 * @brief Запис 16-бітного регістру INA226 (передавальний кабель: MSB -> LSB).
 */
i2c_status_t i2c_write_reg16(uint8_t dev_addr, uint8_t reg_addr, uint16_t value)
{
    /* 1. Очікування вільності шини */
    if (wait_flag(&I2C1_PERIPH->SR2, I2C_SR2_BUSY, false) != I2C_OK) {
        return I2C_ERR_BUSY;
    }

    /* 2. Генерація умови START */
    I2C1_PERIPH->CR1 |= I2C_CR1_START;
    if (wait_flag(&I2C1_PERIPH->SR1, I2C_SR1_SB, true) != I2C_OK) {
        return I2C_ERR_START;
    }

    /* 3. Передача адреси веденого (Slave Addr + Write) */
    I2C1_PERIPH->DR = (uint32_t)(dev_addr << 1) & 0xFEU;
    if (wait_flag(&I2C1_PERIPH->SR1, I2C_SR1_ADDR, true) != I2C_OK) {
        I2C1_PERIPH->CR1 |= I2C_CR1_STOP;
        return I2C_ERR_ADDR;
    }
    (void)I2C1_PERIPH->SR1;
    (void)I2C1_PERIPH->SR2; /* Очищення прапорця ADDR */

    /* 4. Передача адреси регістра */
    if (wait_flag(&I2C1_PERIPH->SR1, I2C_SR1_TXE, true) != I2C_OK) {
        return I2C_ERR_TX;
    }
    I2C1_PERIPH->DR = reg_addr;

    /* 5. Передача Старшого байта (MSB) */
    if (wait_flag(&I2C1_PERIPH->SR1, I2C_SR1_TXE, true) != I2C_OK) {
        return I2C_ERR_TX;
    }
    I2C1_PERIPH->DR = (uint32_t)((value >> 8) & 0xFFU);

    /* 6. Передача Молодшого байта (LSB) */
    if (wait_flag(&I2C1_PERIPH->SR1, I2C_SR1_TXE, true) != I2C_OK) {
        return I2C_ERR_TX;
    }
    I2C1_PERIPH->DR = (uint32_t)(value & 0xFFU);

    /* 7. Очікування завершення передачі останнього байта (BTF) */
    if (wait_flag(&I2C1_PERIPH->SR1, I2C_SR1_BTF, true) != I2C_OK) {
        return I2C_ERR_TX;
    }

    /* 8. Генерація умови STOP */
    I2C1_PERIPH->CR1 |= I2C_CR1_STOP;

    return I2C_OK;
}

/**
 * @brief Читання 16-бітного регістра INA226 (збір MSB та LSB).
 */
i2c_status_t i2c_read_reg16(uint8_t dev_addr, uint8_t reg_addr, uint16_t *value)
{
    if (!value) {
        return I2C_ERR_TX;
    }

    /* 1. Очікування вільності шини */
    if (wait_flag(&I2C1_PERIPH->SR2, I2C_SR2_BUSY, false) != I2C_OK) {
        return I2C_ERR_BUSY;
    }

    /* 2. Звернення до регістра (Write phase) */
    I2C1_PERIPH->CR1 |= I2C_CR1_START;
    if (wait_flag(&I2C1_PERIPH->SR1, I2C_SR1_SB, true) != I2C_OK) {
        return I2C_ERR_START;
    }

    I2C1_PERIPH->DR = (uint32_t)(dev_addr << 1) & 0xFEU;
    if (wait_flag(&I2C1_PERIPH->SR1, I2C_SR1_ADDR, true) != I2C_OK) {
        I2C1_PERIPH->CR1 |= I2C_CR1_STOP;
        return I2C_ERR_ADDR;
    }
    (void)I2C1_PERIPH->SR1;
    (void)I2C1_PERIPH->SR2;

    if (wait_flag(&I2C1_PERIPH->SR1, I2C_SR1_TXE, true) != I2C_OK) {
        return I2C_ERR_TX;
    }
    I2C1_PERIPH->DR = reg_addr;

    if (wait_flag(&I2C1_PERIPH->SR1, I2C_SR1_BTF, true) != I2C_OK) {
        return I2C_ERR_TX;
    }

    /* 3. Повторний запуск (Repeated START) для читання 2 байтів */
    I2C1_PERIPH->CR1 |= I2C_CR1_START;
    if (wait_flag(&I2C1_PERIPH->SR1, I2C_SR1_SB, true) != I2C_OK) {
        return I2C_ERR_START;
    }

    I2C1_PERIPH->DR = (uint32_t)((dev_addr << 1) | 0x01U);
    if (wait_flag(&I2C1_PERIPH->SR1, I2C_SR1_ADDR, true) != I2C_OK) {
        I2C1_PERIPH->CR1 |= I2C_CR1_STOP;
        return I2C_ERR_ADDR;
    }

    /* Вмикаємо підтвердження ACK для прийому 2 байтів */
    I2C1_PERIPH->CR1 |= I2C_CR1_ACK;
    (void)I2C1_PERIPH->SR1;
    (void)I2C1_PERIPH->SR2;

    /* 4. Прийом Старшого байта (MSB) */
    if (wait_flag(&I2C1_PERIPH->SR1, I2C_SR1_RXNE, true) != I2C_OK) {
        return I2C_ERR_RX;
    }
    uint8_t msb = (uint8_t)(I2C1_PERIPH->DR & 0xFFU);

    /* Перед прийомом останнього байта вимикаємо ACK та виставляємо STOP */
    I2C1_PERIPH->CR1 &= ~I2C_CR1_ACK;
    I2C1_PERIPH->CR1 |= I2C_CR1_STOP;

    /* 5. Прийом Молодшого байта (LSB) */
    if (wait_flag(&I2C1_PERIPH->SR1, I2C_SR1_RXNE, true) != I2C_OK) {
        return I2C_ERR_RX;
    }
    uint8_t lsb = (uint8_t)(I2C1_PERIPH->DR & 0xFFU);

    /* 6. Збирання 16-бітного числа (Big-Endian у Little-Endian) */
    *value = ((uint16_t)msb << 8) | (uint16_t)lsb;

    return I2C_OK;
}
