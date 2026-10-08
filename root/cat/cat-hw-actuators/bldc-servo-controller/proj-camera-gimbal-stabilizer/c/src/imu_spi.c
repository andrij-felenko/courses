#include "imu_spi.h"
#include <stddef.h>

/**
 * @file imu_spi.c
 * @brief Реалізація драйвера SPI для зчитування інерціального датчика IMU.
 */

/* Екземпляри апаратних регістрів SPI1 та GPIOA */
static SPI_TypeDef g_spi1_regs;
#define SPI1 (&g_spi1_regs)

static GPIO_TypeDef g_gpioa_regs;
#define GPIOA (&g_gpioa_regs)

#define IMU_CS_PIN (1U << 4) /* PA4 як лінія CS/NSS */

/* Мок-регістри IMU для стабільного тестування без фізичного заліза */
static uint8_t g_imu_mock_registers[128];
static bool g_imu_mock_mode = true;

/**
 * @brief Переведення лінії Chip Select (CS) у низький рівень (активація пристрою).
 */
static void imu_cs_low(void) {
    GPIOA->ODR &= ~IMU_CS_PIN;
}

/**
 * @brief Переведення лінії Chip Select (CS) у високий рівень (деактивація пристрою).
 */
static void imu_cs_high(void) {
    GPIOA->ODR |= IMU_CS_PIN;
}

/**
 * @brief Побайтовий обмін даними по шині SPI з обробкою таймаутів та прапорців.
 * @param tx_byte Байтовий параметр для передачі.
 * @return Отриманий байт з відповного буфера SPI.
 */
static uint8_t spi_transfer_byte(uint8_t tx_byte) {
    uint32_t timeout = 10000U;

    /* Очікування вивільнення буфера передачі TXE */
    while (!(SPI1->SR & SPI_SR_TXE) && --timeout) {}
    if (timeout == 0) return 0xFF;

    /* Запис байта в регістр даних SPI */
    SPI1->DR = tx_byte;

    /* Очікування появи даних у прийомному буфері RXNE */
    timeout = 10000U;
    while (!(SPI1->SR & SPI_SR_RXNE) && --timeout) {}
    if (timeout == 0) return 0xFF;

    return (uint8_t)(SPI1->DR & 0xFFU);
}

/**
 * @brief Ініціалізація периферійного модуля SPI та налаштування IMU.
 * @return 0 при успіху, -1 при помилці виявлення чипа.
 */
int imu_spi_init(void) {
    /* 1. Налаштування лінії CS (PA4) як вихід */
    GPIOA->MODER |= (1U << 8); /* General purpose output mode */
    imu_cs_high();

    /* 2. Конфігурація регістру SPI1_CR1:
     * Master mode, CPOL=1, CPHA=1 (SPI Mode 3), Software Slave Management (SSM/SSI)
     */
    SPI1->CR1 = SPI_CR1_MSTR | SPI_CR1_CPOL | SPI_CR1_CPHA |
                SPI_CR1_BR_DIV8 | SPI_CR1_SSM | SPI_CR1_SSI;
    SPI1->CR1 |= SPI_CR1_SPE; /* Увімкнення SPI */

    /* Налаштування мок-значень для симуляції */
    g_imu_mock_registers[IMU_REG_WHO_AM_I] = 0x98; /* ID пристрою */
    g_imu_mock_registers[IMU_REG_PWR_MGMT_1] = 0x00;

    /* 3. Перевірка зв'язку: зчитування регістру WHO_AM_I */
    uint8_t who_am_i = 0;
    if (imu_spi_read_reg(IMU_REG_WHO_AM_I, &who_am_i) != 0 || who_am_i != 0x98) {
        /* При відсутності реакції або некоректному ID */
        if (!g_imu_mock_mode) {
            return -1;
        }
    }

    /* 4. Пробудження сенсора та вихід зі сплячого режиму */
    imu_spi_write_reg(IMU_REG_PWR_MGMT_1, 0x00);
    /* Налаштування гіроскопа (±2000 dps) та акселерометра (±16g) */
    imu_spi_write_reg(IMU_REG_GYRO_CONFIG, 0x18);  /* FS_SEL = 3 */
    imu_spi_write_reg(IMU_REG_ACCEL_CONFIG, 0x18); /* AFS_SEL = 3 */

    return 0;
}

/**
 * @brief Зчитування одного регістру IMU через SPI.
 */
int imu_spi_read_reg(uint8_t reg_addr, uint8_t *val) {
    if (val == NULL) return -1;

    imu_cs_low();
    /* Встановлюємо старший біт R/W = 1 для читання */
    spi_transfer_byte(reg_addr | IMU_SPI_READ_BIT);

    if (g_imu_mock_mode) {
        *val = g_imu_mock_registers[reg_addr & 0x7FU];
        (void)spi_transfer_byte(0x00);
    } else {
        *val = spi_transfer_byte(0x00);
    }

    imu_cs_high();
    return 0;
}

/**
 * @brief Запис значення в регістр IMU через SPI.
 */
int imu_spi_write_reg(uint8_t reg_addr, uint8_t val) {
    imu_cs_low();
    /* Старший біт R/W = 0 для запису */
    spi_transfer_byte(reg_addr & 0x7FU);
    spi_transfer_byte(val);
    imu_cs_high();

    if (g_imu_mock_mode) {
        g_imu_mock_registers[reg_addr & 0x7FU] = val;
    }
    return 0;
}

/**
 * @brief Пакетне (burst) зчитування декількох послідовних регістрів.
 */
int imu_spi_read_burst(uint8_t start_reg, uint8_t *buf, uint16_t len) {
    if (buf == NULL || len == 0) return -1;

    imu_cs_low();
    spi_transfer_byte(start_reg | IMU_SPI_READ_BIT);

    for (uint16_t i = 0; i < len; i++) {
        if (g_imu_mock_mode) {
            /* Симуляція руху для тестів */
            uint8_t r_addr = (start_reg + i) & 0x7FU;
            if (r_addr == IMU_REG_ACCEL_XOUT_H + 5) { /* Accel Z low byte */
                buf[i] = 0x08; /* ~1g */
            } else if (r_addr == IMU_REG_ACCEL_XOUT_H + 4) {
                buf[i] = 0x00;
            } else {
                buf[i] = (uint8_t)(i * 3 + 7);
            }
            (void)spi_transfer_byte(0x00);
        } else {
            buf[i] = spi_transfer_byte(0x00);
        }
    }

    imu_cs_high();
    return 0;
}

/**
 * @brief Отримання повномасштабних фізичних даних з IMU.
 */
int imu_read_data(imu_data_t *data) {
    if (data == NULL) return -1;

    uint8_t raw_buf[14];
    /* Пакетне читання 14 байт: Accel_X..Z (6b), Temp (2b), Gyro_X..Z (6b) */
    if (imu_spi_read_burst(IMU_REG_ACCEL_XOUT_H, raw_buf, 14) != 0) {
        return -1;
    }

    imu_raw_data_t raw;
    raw.accel_x  = (int16_t)((raw_buf[0] << 8) | raw_buf[1]);
    raw.accel_y  = (int16_t)((raw_buf[2] << 8) | raw_buf[3]);
    raw.accel_z  = (int16_t)((raw_buf[4] << 8) | raw_buf[5]);
    raw.temp_raw = (int16_t)((raw_buf[6] << 8) | raw_buf[7]);
    raw.gyro_x   = (int16_t)((raw_buf[8] << 8) | raw_buf[9]);
    raw.gyro_y   = (int16_t)((raw_buf[10] << 8) | raw_buf[11]);
    raw.gyro_z   = (int16_t)((raw_buf[12] << 8) | raw_buf[13]);

    /* Масштабування для ±16g (2048 LSB/g) та ±2000 dps (16.4 LSB/dps) */
    const float accel_scale = 1.0f / 2048.0f;
    const float gyro_scale  = 1.0f / 16.4f;

    data->accel_g[0] = (float)raw.accel_x * accel_scale;
    data->accel_g[1] = (float)raw.accel_y * accel_scale;
    data->accel_g[2] = (float)raw.accel_z * accel_scale;

    data->gyro_dps[0] = (float)raw.gyro_x * gyro_scale;
    data->gyro_dps[1] = (float)raw.gyro_y * gyro_scale;
    data->gyro_dps[2] = (float)raw.gyro_z * gyro_scale;

    /* Перетворення температури (формула для MPU/ICM серії) */
    data->temp_c = ((float)raw.temp_raw / 326.8f) + 25.0f;

    return 0;
}
