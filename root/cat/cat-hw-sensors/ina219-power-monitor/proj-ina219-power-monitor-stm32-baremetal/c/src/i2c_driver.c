#include "../include/i2c_driver.h"

/**
 * @file i2c_driver.c
 * @brief Прямі маніпуляції реєстрами I2C мікроконтролера STM32.
 */

/* Бітові маски контрольних і статусних регістрів I2C STM32 */
#define I2C_CR1_PE        (1U << 0)   /* Peripheral Enable */
#define I2C_CR1_START     (1U << 8)   /* Start Generation */
#define I2C_CR1_STOP      (1U << 9)   /* Stop Generation */
#define I2C_CR1_ACK       (1U << 10)  /* Acknowledge Enable */
#define I2C_CR1_POS       (1U << 11)  /* Acknowledge/PEC Position */
#define I2C_CR1_SWRST     (1U << 15)  /* Software Reset */

#define I2C_SR1_SB        (1U << 0)   /* Start Bit (Master mode) */
#define I2C_SR1_ADDR      (1U << 1)   /* Address sent (Master mode) */
#define I2C_SR1_BTF       (1U << 2)   /* Byte Transfer Finished */
#define I2C_SR1_ADD10     (1U << 3)   /* 10-bit header sent */
#define I2C_SR1_STOPF     (1U << 4)   /* Stop detection */
#define I2C_SR1_RXNE      (1U << 6)   /* Data Register Not Empty */
#define I2C_SR1_TXE       (1U << 7)   /* Data Register Empty */
#define I2C_SR1_BERR      (1U << 8)   /* Bus Error */
#define I2C_SR1_ARLO      (1U << 9)   /* Arbitration Lost */
#define I2C_SR1_AF        (1U << 10)  /* Acknowledge Failure */
#define I2C_SR1_OVR       (1U << 11)  /* Overrun/Underrun */

#define I2C_SR2_MSL       (1U << 0)   /* Master/Slave mode */
#define I2C_SR2_BUSY      (1U << 1)   /* Bus Busy */
#define I2C_SR2_TRA       (1U << 2)   /* Transmitter/Receiver */

/**
 * @brief Очікує встановлення вказаного прапорця у регістрі з врахуванням таймауту.
 */
static i2c_status_t wait_flag_set(volatile uint32_t *reg, uint32_t flag, uint32_t timeout) {
    while (!(*reg & flag)) {
        if (--timeout == 0) {
            return I2C_ERR_TIMEOUT;
        }
    }
    return I2C_OK;
}

/**
 * @brief Ініціалізує апаратний модуль I2C у режиме Master без використання HAL.
 */
i2c_status_t i2c_init(i2c_bus_t *bus, i2c_reg_t *instance, uint32_t pclk1_hz, uint32_t i2c_speed_hz) {
    if (!bus || !instance || pclk1_hz == 0 || i2c_speed_hz == 0) {
        return I2C_ERR_PARAM;
    }

    bus->instance = instance;
    bus->pclk1_freq_hz = pclk1_hz;
    bus->i2c_speed_hz = i2c_speed_hz;
    bus->timeout_cycles = 100000U;

    /* Вимикаємо периферію для конфігурації */
    bus->instance->CR1 &= ~I2C_CR1_PE;

    /* Програмне скидання стану модуля I2C */
    bus->instance->CR1 |= I2C_CR1_SWRST;
    for (volatile int i = 0; i < 100; i++);
    bus->instance->CR1 &= ~I2C_CR1_SWRST;

    /* Налаштування частоти APB1 в мегагерцах (CR2) */
    uint32_t pclk1_mhz = pclk1_hz / 1000000U;
    bus->instance->CR2 = pclk1_mhz & 0x3FU;

    /* Розрахунок регістру CCR для стандартного режиму (100 кГц) */
    uint32_t ccr_val = pclk1_hz / (i2c_speed_hz * 2U);
    if (ccr_val < 4U) {
        ccr_val = 4U;
    }
    bus->instance->CCR = ccr_val & 0xFFFU;

    /* Максимальний час підйому сигналу TRISE */
    bus->instance->TRISE = (pclk1_mhz + 1U) & 0x3FU;

    /* Увімкнення периферійного модуля I2C */
    bus->instance->CR1 |= I2C_CR1_PE;

    return I2C_OK;
}

/**
 * @brief Формує послідовність START на шині I2C.
 */
i2c_status_t i2c_start(i2c_bus_t *bus) {
    if (!bus || !bus->instance) {
        return I2C_ERR_PARAM;
    }

    /* Генеруємо START умову */
    bus->instance->CR1 |= I2C_CR1_START;

    /* Очікуємо встановлення прапорця SB (Start Bit) у SR1 */
    i2c_status_t status = wait_flag_set(&bus->instance->SR1, I2C_SR1_SB, bus->timeout_cycles);
    if (status != I2C_OK) {
        return I2C_ERR_START_FAIL;
    }

    return I2C_OK;
}

/**
 * @brief Формує послідовність STOP на шині I2C.
 */
i2c_status_t i2c_stop(i2c_bus_t *bus) {
    if (!bus || !bus->instance) {
        return I2C_ERR_PARAM;
    }

    bus->instance->CR1 |= I2C_CR1_STOP;
    return I2C_OK;
}

/**
 * @brief Передає 7-бітну адресу веденого пристрою та напрямок R/W.
 */
i2c_status_t i2c_write_addr(i2c_bus_t *bus, uint8_t dev_addr, bool is_read) {
    if (!bus || !bus->instance) {
        return I2C_ERR_PARAM;
    }

    /* Запис адреси з бітом напрямку (0 - Запис, 1 - Читання) */
    uint32_t addr_byte = (dev_addr << 1) | (is_read ? 1U : 0U);
    bus->instance->DR = addr_byte;

    /* Чекаємо встановлення ADDR або збою ACK (AF) */
    uint32_t timeout = bus->timeout_cycles;
    while (!(bus->instance->SR1 & (I2C_SR1_ADDR | I2C_SR1_AF))) {
        if (--timeout == 0) {
            return I2C_ERR_TIMEOUT;
        }
    }

    /* Обробка відсутності відгуку (NACK) */
    if (bus->instance->SR1 & I2C_SR1_AF) {
        bus->instance->SR1 &= ~I2C_SR1_AF;
        i2c_stop(bus);
        return I2C_ERR_ADDR_NACK;
    }

    /* Очищення прапорця ADDR послідовним зчитуванням SR1, а потім SR2 */
    (void)bus->instance->SR1;
    (void)bus->instance->SR2;

    return I2C_OK;
}

/**
 * @brief Записує послідовність байтів починаючи з регістру reg_addr.
 */
i2c_status_t i2c_write_bytes(i2c_bus_t *bus, uint8_t dev_addr, uint8_t reg_addr, const uint8_t *data, size_t len) {
    if (!bus || !data) {
        return I2C_ERR_PARAM;
    }

    i2c_status_t status = i2c_start(bus);
    if (status != I2C_OK) {
        return status;
    }

    status = i2c_write_addr(bus, dev_addr, false);
    if (status != I2C_OK) {
        return status;
    }

    /* Передаємо адресний вказівник регістру */
    status = wait_flag_set(&bus->instance->SR1, I2C_SR1_TXE, bus->timeout_cycles);
    if (status != I2C_OK) {
        i2c_stop(bus);
        return status;
    }
    bus->instance->DR = reg_addr;

    /* Передаємо масив даних */
    for (size_t i = 0; i < len; i++) {
        status = wait_flag_set(&bus->instance->SR1, I2C_SR1_TXE, bus->timeout_cycles);
        if (status != I2C_OK) {
            i2c_stop(bus);
            return status;
        }
        bus->instance->DR = data[i];

        if (bus->instance->SR1 & I2C_SR1_AF) {
            bus->instance->SR1 &= ~I2C_SR1_AF;
            i2c_stop(bus);
            return I2C_ERR_DATA_NACK;
        }
    }

    /* Очікуємо завершення передачі останнього байта (BTF) */
    status = wait_flag_set(&bus->instance->SR1, I2C_SR1_BTF, bus->timeout_cycles);
    i2c_stop(bus);

    return status;
}

/**
 * @brief Зчитує послідовність байтів з 16-бітного регістру INA219.
 */
i2c_status_t i2c_read_bytes(i2c_bus_t *bus, uint8_t dev_addr, uint8_t reg_addr, uint8_t *data, size_t len) {
    if (!bus || !data || len == 0) {
        return I2C_ERR_PARAM;
    }

    /* 1. Запис адреси регістру */
    i2c_status_t status = i2c_start(bus);
    if (status != I2C_OK) {
        return status;
    }

    status = i2c_write_addr(bus, dev_addr, false);
    if (status != I2C_OK) {
        return status;
    }

    status = wait_flag_set(&bus->instance->SR1, I2C_SR1_TXE, bus->timeout_cycles);
    if (status != I2C_OK) {
        i2c_stop(bus);
        return status;
    }
    bus->instance->DR = reg_addr;

    status = wait_flag_set(&bus->instance->SR1, I2C_SR1_BTF, bus->timeout_cycles);
    if (status != I2C_OK) {
        i2c_stop(bus);
        return status;
    }

    /* 2. Повторний START і перемикання на читання */
    status = i2c_start(bus);
    if (status != I2C_OK) {
        return status;
    }

    /* Для 2-байтного читання (16-бітний регістр INA219) налаштовуємо апаратний ACK/POS */
    if (len == 2) {
        bus->instance->CR1 |= I2C_CR1_ACK;
        bus->instance->CR1 |= I2C_CR1_POS;

        /* Відправляємо адресу веденого у режимі читання */
        status = i2c_write_addr(bus, dev_addr, true);
        if (status != I2C_OK) {
            bus->instance->CR1 &= ~I2C_CR1_POS;
            return status;
        }

        /* Вимикаємо ACK перед читанням двобайтової послідовності */
        bus->instance->CR1 &= ~I2C_CR1_ACK;

        /* Очікуємо BTF (обидва байти прийняті у DR і зсувний регістр) */
        status = wait_flag_set(&bus->instance->SR1, I2C_SR1_BTF, bus->timeout_cycles);
        if (status != I2C_OK) {
            bus->instance->CR1 &= ~I2C_CR1_POS;
            i2c_stop(bus);
            return status;
        }

        /* Формуємо STOP перед зчитанням DR */
        i2c_stop(bus);

        data[0] = (uint8_t)bus->instance->DR; /* MSB */
        data[1] = (uint8_t)bus->instance->DR; /* LSB */

        bus->instance->CR1 &= ~I2C_CR1_POS;
        return I2C_OK;
    }

    /* Загальне багатобайтне читання */
    bus->instance->CR1 |= I2C_CR1_ACK;
    status = i2c_write_addr(bus, dev_addr, true);
    if (status != I2C_OK) {
        return status;
    }

    for (size_t i = 0; i < len; i++) {
        if (i == len - 1) {
            bus->instance->CR1 &= ~I2C_CR1_ACK;
            i2c_stop(bus);
        }

        status = wait_flag_set(&bus->instance->SR1, I2C_SR1_RXNE, bus->timeout_cycles);
        if (status != I2C_OK) {
            return status;
        }

        data[i] = (uint8_t)bus->instance->DR;
    }

    return I2C_OK;
}

/**
 * @brief Виконує прямий запис 16-бітного регістру із перетворенням у MSB/LSB порядок (Big-Endian).
 */
i2c_status_t i2c_write_reg16(i2c_bus_t *bus, uint8_t dev_addr, uint8_t reg_addr, uint16_t value) {
    uint8_t buf[2];
    buf[0] = (uint8_t)((value >> 8) & 0xFFU); /* MSB перший */
    buf[1] = (uint8_t)(value & 0xFFU);        /* LSB другий */

    return i2c_write_bytes(bus, dev_addr, reg_addr, buf, 2);
}

/**
 * @brief Виконує прямо зчитання 16-бітного регістру та повертає значення у форматі host-endianness.
 */
i2c_status_t i2c_read_reg16(i2c_bus_t *bus, uint8_t dev_addr, uint8_t reg_addr, uint16_t *value) {
    if (!value) {
        return I2C_ERR_PARAM;
    }

    uint8_t buf[2] = {0, 0};
    i2c_status_t status = i2c_read_bytes(bus, dev_addr, reg_addr, buf, 2);
    if (status == I2C_OK) {
        *value = (uint16_t)(((uint16_t)buf[0] << 8) | buf[1]);
    }

    return status;
}
