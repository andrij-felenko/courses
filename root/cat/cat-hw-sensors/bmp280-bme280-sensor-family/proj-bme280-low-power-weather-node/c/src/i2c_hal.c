#include "i2c_hal.h"
#include <stdio.h>
#include <string.h>

/**
 * @file i2c_hal.c
 * @brief Реалізація низькорівневих шинних операцій I2C.
 * 
 * Демонструє контроль периферійних регістрів I2C мікроконтролера: генерацію 
 * сигналів START/STOP, перевірку ACK/NACK, контроль прапорців буферів TXE/RXNE,
 * обробку таймаутів та апаратну симуляцію шинних регістрів BME280 для тестування.
 */

/* Макет периферійних регістрів I2C Master хост-контролера */
typedef struct {
    volatile uint32_t CR1;   /*!< Control Register 1 (START, STOP, PE, ACK) */
    volatile uint32_t CR2;   /*!< Control Register 2 (FREQ, IT) */
    volatile uint32_t OAR1;  /*!< Own Address Register 1 */
    volatile uint32_t DR;    /*!< Data Register (TXE/RXNE) */
    volatile uint32_t SR1;   /*!< Status Register 1 (SB, ADDR, BTF, TXE, RXNE, AF) */
    volatile uint32_t SR2;   /*!< Status Register 2 (BUSY, MSL) */
} i2c_hardware_regs_t;

/* Бітові маски статусних регістрів I2C HAL */
#define I2C_SR1_SB   (1 << 0)  /*!< Start Bit generated */
#define I2C_SR1_ADDR (1 << 1)  /*!< Address sent/matched */
#define I2C_SR1_BTF  (1 << 2)  /*!< Byte Transfer Finished */
#define I2C_SR1_TXE  (1 << 7)  /*!< Data Register Empty (Transmit) */
#define I2C_SR1_RXNE (1 << 6)  /*!< Data Register Not Empty (Receive) */
#define I2C_SR1_AF   (1 << 10) /*!< Acknowledge Failure (NACK) */

#define I2C_SR2_BUSY (1 << 1)  /*!< Bus Busy flag */

static i2c_hardware_regs_t s_i2c_regs;
static bool s_hal_initialized = false;
static uint32_t s_system_ticks_ms = 0;

/* Карта пам'яті симульованого веденого давача BME280 */
static uint8_t s_bme280_nvm_registers[256];

static void init_bme280_simulated_nvm(void) {
    memset(s_bme280_nvm_registers, 0, sizeof(s_bme280_nvm_registers));

    /* 0xD0: Chip ID = 0x60 */
    s_bme280_nvm_registers[0xD0] = 0x60;

    /* Блок 1 (0x88..0xA1): Калібрувальні коефіцієнти T1..T3, P1..P9, H1 */
    /* dig_T1 = 27504 (0x6B70) */
    s_bme280_nvm_registers[0x88] = 0x70;
    s_bme280_nvm_registers[0x89] = 0x6B;
    /* dig_T2 = 26435 (0x6743) */
    s_bme280_nvm_registers[0x8A] = 0x43;
    s_bme280_nvm_registers[0x8B] = 0x67;
    /* dig_T3 = -1000 (0xFC18) */
    s_bme280_nvm_registers[0x8C] = 0x18;
    s_bme280_nvm_registers[0x8D] = 0xFC;

    /* dig_P1 = 36477 (0x8E7D) */
    s_bme280_nvm_registers[0x8E] = 0x7D;
    s_bme280_nvm_registers[0x8F] = 0x8E;
    /* dig_P2 = -10685 (0xD633) */
    s_bme280_nvm_registers[0x90] = 0x33;
    s_bme280_nvm_registers[0x91] = 0xD6;
    /* dig_P3 = 3024 (0x0BD0) */
    s_bme280_nvm_registers[0x92] = 0xD0;
    s_bme280_nvm_registers[0x93] = 0x0B;
    /* dig_P4 = 2855 (0x0B27) */
    s_bme280_nvm_registers[0x94] = 0x27;
    s_bme280_nvm_registers[0x95] = 0x0B;
    /* dig_P5 = 140 (0x008C) */
    s_bme280_nvm_registers[0x96] = 0x8C;
    s_bme280_nvm_registers[0x97] = 0x00;
    /* dig_P6 = -7 (0xFFF9) */
    s_bme280_nvm_registers[0x98] = 0xF9;
    s_bme280_nvm_registers[0x99] = 0xFF;
    /* dig_P7 = 15500 (0x3C8C) */
    s_bme280_nvm_registers[0x9A] = 0x8C;
    s_bme280_nvm_registers[0x9B] = 0x3C;
    /* dig_P8 = -14600 (0xC6F8) */
    s_bme280_nvm_registers[0x9C] = 0xF8;
    s_bme280_nvm_registers[0x9D] = 0xC6;
    /* dig_P9 = 6000 (0x1770) */
    s_bme280_nvm_registers[0x9E] = 0x70;
    s_bme280_nvm_registers[0x9F] = 0x17;

    /* dig_H1 = 75 (0x4B) */
    s_bme280_nvm_registers[0xA1] = 0x4B;

    /* Блок 2 (0xE1..0xE7): Калібрувальні коефіцієнти H2..H6 */
    /* dig_H2 = 362 (0x016A) */
    s_bme280_nvm_registers[0xE1] = 0x6A;
    s_bme280_nvm_registers[0xE2] = 0x01;
    /* dig_H3 = 0 */
    s_bme280_nvm_registers[0xE3] = 0x00;
    /* dig_H4 = 313 (0x0139) -> E4=0x13, E5[3:0]=0x09 */
    s_bme280_nvm_registers[0xE4] = 0x13;
    /* dig_H5 = 50 (0x0032) -> E6=0x03, E5[7:4]=0x02 */
    s_bme280_nvm_registers[0xE5] = 0x29; /* (0x02 << 4) | (0x09 & 0x0F) = 0x29 */
    s_bme280_nvm_registers[0xE6] = 0x03;
    /* dig_H6 = 30 (0x1E) */
    s_bme280_nvm_registers[0xE7] = 0x1E;

    /* Початкові значення сирих відліків АЦП (0xF7..0xFE) */
    /* Pressure raw = 415148 (0x655AC) -> MSB=0x65, LSB=0x5A, XLSB=0xC0 */
    s_bme280_nvm_registers[0xF7] = 0x65;
    s_bme280_nvm_registers[0xF8] = 0x5A;
    s_bme280_nvm_registers[0xF9] = 0xC0;

    /* Temperature raw = 519888 (0x7EEB0) -> MSB=0x7E, LSB=0xEB, XLSB=0x00 */
    s_bme280_nvm_registers[0xFA] = 0x7E;
    s_bme280_nvm_registers[0xFB] = 0xEB;
    s_bme280_nvm_registers[0xFC] = 0x00;

    /* Humidity raw = 32312 (0x7E38) -> MSB=0x7E, LSB=0x38 */
    s_bme280_nvm_registers[0xFD] = 0x7E;
    s_bme280_nvm_registers[0xFE] = 0x38;
}

i2c_hal_err_t i2c_hal_init(uint32_t clock_speed_hz) {
    (void)clock_speed_hz;

    s_i2c_regs.CR1 = 0x0001; /* Enable Peripheral (PE = 1) */
    s_i2c_regs.SR1 = I2C_SR1_TXE;
    s_i2c_regs.SR2 = 0;

    init_bme280_simulated_nvm();
    s_hal_initialized = true;

    return I2C_HAL_OK;
}

void i2c_hal_delay_ms(uint32_t ms) {
    s_system_ticks_ms += ms;
}

uint32_t i2c_hal_get_ticks_ms(void) {
    return s_system_ticks_ms;
}

/* Внутрішній метод очікування шинного прапорця у статусному регістрі SR1 */
static i2c_hal_err_t wait_for_flag(uint32_t flag_mask, bool set_state, uint32_t timeout_ms) {
    uint32_t start_time = s_system_ticks_ms;
    while ((s_system_ticks_ms - start_time) < timeout_ms) {
        bool is_set = ((s_i2c_regs.SR1 & flag_mask) != 0);
        if (is_set == set_state) {
            return I2C_HAL_OK;
        }
        if ((s_i2c_regs.SR1 & I2C_SR1_AF) != 0) {
            s_i2c_regs.SR1 &= ~I2C_SR1_AF;
            return I2C_HAL_ERR_NACK;
        }
        i2c_hal_delay_ms(1);
    }
    return I2C_HAL_ERR_TIMEOUT;
}

i2c_hal_err_t i2c_hal_write_reg(uint8_t dev_addr, uint8_t reg_addr, uint8_t data) {
    if (!s_hal_initialized) {
        return I2C_HAL_ERR_NULL_PTR;
    }

    if (dev_addr != BME280_I2C_ADDR_PRIM && dev_addr != BME280_I2C_ADDR_SEC) {
        return I2C_HAL_ERR_NACK;
    }

    /* 1. Генерація сигналу START */
    s_i2c_regs.CR1 |= (1 << 8); /* START bit */
    s_i2c_regs.SR1 |= I2C_SR1_SB;

    if (wait_for_flag(I2C_SR1_SB, true, I2C_HAL_DEFAULT_TIMEOUT_MS) != I2C_HAL_OK) {
        return I2C_HAL_ERR_TIMEOUT;
    }

    /* 2. Передача адреси веденого пристрою з прапорцем запису (Write = 0) */
    s_i2c_regs.DR = (dev_addr << 1) | 0;
    s_i2c_regs.SR1 |= I2C_SR1_ADDR | I2C_SR1_TXE;

    /* 3. Передача адреси регістру BME280 */
    s_i2c_regs.DR = reg_addr;

    /* 4. Передача байта даних */
    s_i2c_regs.DR = data;
    s_bme280_nvm_registers[reg_addr] = data;

    /* Реакція симульованого пристрою на запис у ctrl_meas (0xF4) */
    if (reg_addr == BME280_REG_CTRL_MEAS) {
        uint8_t mode = data & 0x03;
        if (mode == BME280_MODE_FORCED) {
            /* Запуск поодинокого вимірювання: встановлюємо прапорець measuring (0x08) */
            s_bme280_nvm_registers[BME280_REG_STATUS] |= BME280_STATUS_MEASURING_MSK;
        }
    }

    /* 5. Генерація сигналу STOP */
    s_i2c_regs.CR1 |= (1 << 9); /* STOP bit */
    s_i2c_regs.SR1 &= ~I2C_SR1_SB;

    return I2C_HAL_OK;
}

i2c_hal_err_t i2c_hal_read_reg(uint8_t dev_addr, uint8_t reg_addr, uint8_t *out_data) {
    return i2c_hal_read_bytes(dev_addr, reg_addr, out_data, 1);
}

i2c_hal_err_t i2c_hal_read_bytes(uint8_t dev_addr, uint8_t start_reg, uint8_t *buffer, size_t len) {
    if (!s_hal_initialized || buffer == NULL || len == 0) {
        return I2C_HAL_ERR_NULL_PTR;
    }

    if (dev_addr != BME280_I2C_ADDR_PRIM && dev_addr != BME280_I2C_ADDR_SEC) {
        return I2C_HAL_ERR_NACK;
    }

    /* 1. Фаза встановлення вказівника регістру (START + DevAddr W + RegAddr) */
    s_i2c_regs.CR1 |= (1 << 8);
    s_i2c_regs.SR1 |= I2C_SR1_SB;

    s_i2c_regs.DR = (dev_addr << 1) | 0;
    s_i2c_regs.DR = start_reg;

    /* 2. Повторний старт (Repeated START) та зміна напрямку на читання (DevAddr R = 1) */
    s_i2c_regs.CR1 |= (1 << 8);
    s_i2c_regs.DR = (dev_addr << 1) | 1;
    s_i2c_regs.SR1 |= I2C_SR1_ADDR | I2C_SR1_RXNE;

    /*
     * Якщо статус давача опитується і замір було запущено у Forced Mode,
     * симулюємо завершення оцифровки АЦП після 5 мс.
     */
    if (start_reg == BME280_REG_STATUS) {
        static uint32_t poll_count = 0;
        poll_count++;
        if (poll_count >= 2) {
            s_bme280_nvm_registers[BME280_REG_STATUS] &= ~BME280_STATUS_MEASURING_MSK;
            poll_count = 0;
        }
    }

    /* 3. Послідовне вичитання байтів (burst read) із масиву регістрів */
    for (size_t i = 0; i < len; i++) {
        uint8_t current_reg = (uint8_t)(start_reg + i);
        buffer[i] = s_bme280_nvm_registers[current_reg];
        s_i2c_regs.DR = buffer[i];
    }

    /* 4. Генерація STOP сигналу */
    s_i2c_regs.CR1 |= (1 << 9);

    return I2C_HAL_OK;
}

const char* i2c_hal_err_to_str(i2c_hal_err_t err) {
    switch (err) {
        case I2C_HAL_OK:
            return "Шинна транзакція успішна (OK)";
        case I2C_HAL_ERR_NULL_PTR:
            return "Недійсний буфер даних або незаініціалізований HAL";
        case I2C_HAL_ERR_TIMEOUT:
            return "Таймаут очікування прапорця буфера TXE/RXNE";
        case I2C_HAL_ERR_NACK:
            return "Відсутність квитування пристрою (NACK)";
        case I2C_HAL_ERR_BUS_BUSY:
            return "Шина I2C зайнята (BUSY)";
        case I2C_HAL_ERR_ARBITRATION_LOST:
            return "Втрачено арбітраж I2C Master";
        default:
            return "Невідома помилка шини";
    }
}
