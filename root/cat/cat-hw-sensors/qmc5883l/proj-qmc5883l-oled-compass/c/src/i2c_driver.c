#include "i2c_driver.h"
#include <string.h>

/**
 * @file i2c_driver.c
 * @brief Реалізація низькорівневих шинних операцій I2C для мікроконтролера.
 */

#define I2C_DEFAULT_TIMEOUT_MS 100U

/* Структура регістрів апаратного периферийного модуля I2C */
typedef struct {
    volatile uint32_t CR1;   /**< Control register 1 */
    volatile uint32_t CR2;   /**< Control register 2 */
    volatile uint32_t OAR1;  /**< Own address register 1 */
    volatile uint32_t OAR2;  /**< Own address register 2 */
    volatile uint32_t DR;    /**< Data register */
    volatile uint32_t SR1;   /**< Status register 1 */
    volatile uint32_t SR2;   /**< Status register 2 */
    volatile uint32_t CCR;   /**< Clock control register */
    volatile uint32_t TRISE; /**< TRISE register */
} i2c_hw_registers_t;

/* Маски бітів регістрів I2C */
#define I2C_CR1_PE          (1U << 0)
#define I2C_CR1_START       (1U << 8)
#define I2C_CR1_STOP        (1U << 9)
#define I2C_CR1_ACK         (1U << 10)
#define I2C_CR1_SWRST       (1U << 15)

#define I2C_SR1_SB          (1U << 0)
#define I2C_SR1_ADDR        (1U << 1)
#define I2C_SR1_BTF         (1U << 2)
#define I2C_SR1_ADDR10      (1U << 3)
#define I2C_SR1_STOPF       (1U << 4)
#define I2C_SR1_RXNE        (1U << 6)
#define I2C_SR1_TXE         (1U << 7)
#define I2C_SR1_BERR        (1U << 8)
#define I2C_SR1_ARLO        (1U << 9)
#define I2C_SR1_AF          (1U << 10)
#define I2C_SR1_OVR         (1U << 11)
#define I2C_SR1_TIMEOUT     (1U << 14)

#define I2C_SR2_BUSY        (1U << 0)
#define I2C_SR2_MSL         (1U << 1)

/* Симуляція периферийного блока I2C */
static i2c_hw_registers_t i2c_instance;
static i2c_hw_registers_t *const I2C_PERIPH = &i2c_instance;
static bool s_driver_initialized = false;

/* Допоміжна функція очікування прапорця SR1 */
static i2c_status_t wait_sr1_flag(uint32_t flag, bool state, uint32_t timeout_ms) {
    uint32_t loops = timeout_ms * 1000U;
    while (loops > 0) {
        bool current_state = (I2C_PERIPH->SR1 & flag) != 0U;
        if (current_state == state) {
            return I2C_OK;
        }
        if (I2C_PERIPH->SR1 & I2C_SR1_AF) {
            I2C_PERIPH->SR1 &= ~I2C_SR1_AF;
            return I2C_ERR_NACK;
        }
        loops--;
    }
    return I2C_ERR_TIMEOUT;
}

i2c_status_t i2c_init(i2c_speed_t speed) {
    if (speed != I2C_SPEED_STANDARD && speed != I2C_SPEED_FAST) {
        return I2C_ERR_PARAM;
    }

    /* Скидання периферийного блоку */
    I2C_PERIPH->CR1 |= I2C_CR1_SWRST;
    I2C_PERIPH->CR1 &= ~I2C_CR1_SWRST;

    /* Конфігурація тактування (APB1 = 16 МГц) */
    I2C_PERIPH->CR2 = 16U; 

    if (speed == I2C_SPEED_STANDARD) {
        I2C_PERIPH->CCR = 80U;  /* 100 kHz */
        I2C_PERIPH->TRISE = 17U;
    } else {
        I2C_PERIPH->CCR = 0x801A; /* 400 kHz Fast Mode */
        I2C_PERIPH->TRISE = 6U;
    }

    /* Увімкнення модуля */
    I2C_PERIPH->CR1 |= I2C_CR1_PE;
    I2C_PERIPH->SR1 = 0;
    I2C_PERIPH->SR2 = 0;

    s_driver_initialized = true;
    return I2C_OK;
}

i2c_status_t i2c_write(uint8_t dev_addr, const uint8_t *data, size_t len, uint32_t timeout_ms) {
    if (!s_driver_initialized || data == NULL || len == 0) {
        return I2C_ERR_PARAM;
    }

    /* Перевірка зайнятості шини */
    if (I2C_PERIPH->SR2 & I2C_SR2_BUSY) {
        /* Дозволяємо повторну спробу якщо попередній STOP завершено */
    }

    /* Генерація START */
    I2C_PERIPH->CR1 |= I2C_CR1_START;
    i2c_status_t status = wait_sr1_flag(I2C_SR1_SB, true, timeout_ms);
    if (status != I2C_OK) return status;

    /* Відправка адреси з бітом запису (R/W = 0) */
    I2C_PERIPH->DR = (dev_addr << 1) & 0xFE;
    status = wait_sr1_flag(I2C_SR1_ADDR, true, timeout_ms);
    if (status != I2C_OK) {
        I2C_PERIPH->CR1 |= I2C_CR1_STOP;
        return status;
    }

    /* Очищення прапорця ADDR за допомогою читання SR2 */
    (void)I2C_PERIPH->SR2;

    /* Відправка даних */
    for (size_t i = 0; i < len; i++) {
        status = wait_sr1_flag(I2C_SR1_TXE, true, timeout_ms);
        if (status != I2C_OK) {
            I2C_PERIPH->CR1 |= I2C_CR1_STOP;
            return status;
        }
        I2C_PERIPH->DR = data[i];
    }

    /* Очікування завершення передачі останнього байта (BTF) */
    status = wait_sr1_flag(I2C_SR1_BTF, true, timeout_ms);
    
    /* Генерація STOP */
    I2C_PERIPH->CR1 |= I2C_CR1_STOP;

    return I2C_OK;
}

i2c_status_t i2c_read(uint8_t dev_addr, uint8_t *data, size_t len, uint32_t timeout_ms) {
    if (!s_driver_initialized || data == NULL || len == 0) {
        return I2C_ERR_PARAM;
    }

    /* Увімкнення підтвердження ACK */
    I2C_PERIPH->CR1 |= I2C_CR1_ACK;

    /* Генерація START */
    I2C_PERIPH->CR1 |= I2C_CR1_START;
    i2c_status_t status = wait_sr1_flag(I2C_SR1_SB, true, timeout_ms);
    if (status != I2C_OK) return status;

    /* Відправка адреси з бітом читання (R/W = 1) */
    I2C_PERIPH->DR = (dev_addr << 1) | 0x01;
    status = wait_sr1_flag(I2C_SR1_ADDR, true, timeout_ms);
    if (status != I2C_OK) {
        I2C_PERIPH->CR1 |= I2C_CR1_STOP;
        return status;
    }

    if (len == 1) {
        /* Для 1 байта вимикаємо ACK до очищення ADDR */
        I2C_PERIPH->CR1 &= ~I2C_CR1_ACK;
        (void)I2C_PERIPH->SR2;
        I2C_PERIPH->CR1 |= I2C_CR1_STOP;

        status = wait_sr1_flag(I2C_SR1_RXNE, true, timeout_ms);
        if (status != I2C_OK) return status;
        data[0] = (uint8_t)I2C_PERIPH->DR;
    } else {
        (void)I2C_PERIPH->SR2;
        for (size_t i = 0; i < len; i++) {
            if (i == len - 1) {
                /* Перед останнім байтом вимикаємо ACK та формуємо STOP */
                I2C_PERIPH->CR1 &= ~I2C_CR1_ACK;
                I2C_PERIPH->CR1 |= I2C_CR1_STOP;
            }
            status = wait_sr1_flag(I2C_SR1_RXNE, true, timeout_ms);
            if (status != I2C_OK) return status;
            data[i] = (uint8_t)I2C_PERIPH->DR;
        }
    }

    return I2C_OK;
}

i2c_status_t i2c_write_reg(uint8_t dev_addr, uint8_t reg_addr, uint8_t value) {
    uint8_t pkt[2] = { reg_addr, value };
    return i2c_write(dev_addr, pkt, 2, I2C_DEFAULT_TIMEOUT_MS);
}

i2c_status_t i2c_read_reg(uint8_t dev_addr, uint8_t reg_addr, uint8_t *value) {
    return i2c_read_regs(dev_addr, reg_addr, value, 1);
}

i2c_status_t i2c_read_regs(uint8_t dev_addr, uint8_t reg_addr, uint8_t *buffer, size_t len) {
    if (buffer == NULL || len == 0) return I2C_ERR_PARAM;

    /* Запис адреси регістра */
    i2c_status_t status = i2c_write(dev_addr, &reg_addr, 1, I2C_DEFAULT_TIMEOUT_MS);
    if (status != I2C_OK) return status;

    /* Повторне зчитування блоку даних */
    return i2c_read(dev_addr, buffer, len, I2C_DEFAULT_TIMEOUT_MS);
}

bool i2c_ping(uint8_t dev_addr) {
    if (!s_driver_initialized) return false;

    I2C_PERIPH->CR1 |= I2C_CR1_START;
    if (wait_sr1_flag(I2C_SR1_SB, true, 10) != I2C_OK) return false;

    I2C_PERIPH->DR = (dev_addr << 1) & 0xFE;
    i2c_status_t status = wait_sr1_flag(I2C_SR1_ADDR, true, 10);

    I2C_PERIPH->CR1 |= I2C_CR1_STOP;
    (void)I2C_PERIPH->SR2;

    return (status == I2C_OK);
}
