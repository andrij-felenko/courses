#ifndef IMU_SPI_H
#define IMU_SPI_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @file imu_spi.h
 * @brief Низькорівневий SPI-драйвер для зчитування інерціального модуля (IMU).
 */

/* Структури периферії MCU (SPI та GPIO) */
typedef struct {
    volatile uint32_t CR1;     /**< Control register 1 */
    volatile uint32_t CR2;     /**< Control register 2 */
    volatile uint32_t SR;      /**< Status register */
    volatile uint32_t DR;      /**< Data register */
    volatile uint32_t CRCPR;   /**< CRC polynomial register */
    volatile uint32_t RXCRCR;  /**< Rx CRC register */
    volatile uint32_t TXCRCR;  /**< Tx CRC register */
} SPI_TypeDef;

typedef struct {
    volatile uint32_t MODER;   /**< Mode register */
    volatile uint32_t OTYPER;  /**< Output type register */
    volatile uint32_t OSPEEDR; /**< Output speed register */
    volatile uint32_t PUPDR;   /**< Pull-up/pull-down register */
    volatile uint32_t IDR;     /**< Input data register */
    volatile uint32_t ODR;     /**< Output data register */
    volatile uint32_t BSRR;    /**< Bit set/reset register */
    volatile uint32_t LCKR;    /**< Configuration lock register */
} GPIO_TypeDef;

/* Прапорці регістру SPI_SR */
#define SPI_SR_RXNE         (1U << 0)  /**< Receive buffer not empty */
#define SPI_SR_TXE          (1U << 1)  /**< Transmit buffer empty */
#define SPI_SR_BSY          (1U << 7)  /**< Busy flag */

/* Біти регістру SPI_CR1 */
#define SPI_CR1_CPHA        (1U << 0)  /**< Clock phase */
#define SPI_CR1_CPOL        (1U << 1)  /**< Clock polarity */
#define SPI_CR1_MSTR        (1U << 2)  /**< Master selection */
#define SPI_CR1_BR_DIV8     (2U << 3)  /**< Baud rate control (f_PCLK/8) */
#define SPI_CR1_SPE         (1U << 6)  /**< SPI enable */
#define SPI_CR1_SSI         (1U << 8)  /**< Internal slave select */
#define SPI_CR1_SSM         (1U << 9)  /**< Software slave management */

/* Адреси регістрів IMU (ICM/MPU серія) */
#define IMU_SPI_READ_BIT    0x80U
#define IMU_REG_WHO_AM_I    0x75U
#define IMU_REG_PWR_MGMT_1  0x6BU
#define IMU_REG_CONFIG      0x1AU
#define IMU_REG_GYRO_CONFIG 0x1BU
#define IMU_REG_ACCEL_CONFIG 0x1CU
#define IMU_REG_ACCEL_XOUT_H 0x3BU

/**
 * @brief Сирі (16-бітні) значення з сенсорів IMU.
 */
typedef struct {
    int16_t accel_x;
    int16_t accel_y;
    int16_t accel_z;
    int16_t temp_raw;
    int16_t gyro_x;
    int16_t gyro_y;
    int16_t gyro_z;
} imu_raw_data_t;

/**
 * @brief Фізичні калібровані значення IMU.
 */
typedef struct {
    float accel_g[3];   /**< Прискорення по осях X, Y, Z (в g) */
    float gyro_dps[3];  /**< Кутова швидкість по осях X, Y, Z (в град/с) */
    float temp_c;       /**< Температура чипа (град. Цельсія) */
} imu_data_t;

/* Прототипи функцій */
int imu_spi_init(void);
int imu_spi_read_reg(uint8_t reg_addr, uint8_t *val);
int imu_spi_write_reg(uint8_t reg_addr, uint8_t val);
int imu_spi_read_burst(uint8_t start_reg, uint8_t *buf, uint16_t len);
int imu_read_data(imu_data_t *data);

#endif /* IMU_SPI_H */
