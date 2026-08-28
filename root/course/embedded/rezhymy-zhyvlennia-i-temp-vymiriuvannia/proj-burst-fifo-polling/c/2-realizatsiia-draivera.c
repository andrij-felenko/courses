#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include "stm32l4xx_hal.h"

#define SENSOR_FIFO_WATERMARK    32
#define SENSOR_FRAME_SIZE        6   /* 2 байти на кожну з осей X, Y, Z */
#define SENSOR_BURST_BUFFER_SIZE (SENSOR_FIFO_WATERMARK * SENSOR_FRAME_SIZE)

#define REG_FIFO_CTRL            0x2E
#define REG_FIFO_SRC             0x2F
#define REG_FIFO_DATA_OUT        0x28
#define REG_INT1_CTRL            0x22
#define REG_CTRL_REG1            0x20

#define SPI_READ_BIT             0x80
#define SPI_AUTO_INCR_BIT        0x40

typedef struct {
    int16_t x;
    int16_t y;
    int16_t z;
} SensorSample;

typedef struct {
    SPI_HandleTypeDef *hspi;
    GPIO_TypeDef *cs_port;
    uint16_t cs_pin;
    volatile bool data_ready_flag;
    uint8_t rx_raw_buffer[SENSOR_BURST_BUFFER_SIZE + 1];
    uint8_t tx_dummy_buffer[SENSOR_BURST_BUFFER_SIZE + 1];
    SensorSample parsed_samples[SENSOR_FIFO_WATERMARK];
} SensorFifoDriver;

static inline void sensor_cs_low(SensorFifoDriver *dev) {
    HAL_GPIO_WritePin(dev->cs_port, dev->cs_pin, GPIO_PIN_RESET);
}

static inline void sensor_cs_high(SensorFifoDriver *dev) {
    HAL_GPIO_WritePin(dev->cs_port, dev->cs_pin, GPIO_PIN_SET);
}

HAL_StatusTypeDef sensor_write_reg(SensorFifoDriver *dev, uint8_t reg, uint8_t val) {
    uint8_t tx[2] = { reg & ~SPI_READ_BIT, val };
    sensor_cs_low(dev);
    HAL_StatusTypeDef status = HAL_SPI_Transmit(dev->hspi, tx, 2, HAL_MAX_DELAY);
    sensor_cs_high(dev);
    return status;
}

HAL_StatusTypeDef sensor_read_reg(SensorFifoDriver *dev, uint8_t reg, uint8_t *val) {
    uint8_t tx[2] = { reg | SPI_READ_BIT, 0x00 };
    uint8_t rx[2] = { 0 };
    sensor_cs_low(dev);
    HAL_StatusTypeDef status = HAL_SPI_TransmitReceive(dev->hspi, tx, rx, 2, HAL_MAX_DELAY);
    sensor_cs_high(dev);
    if (status == HAL_OK) {
        *val = rx[1];
    }
    return status;
}

HAL_StatusTypeDef sensor_fifo_init(SensorFifoDriver *dev) {
    /* 1. Налаштування порогу Watermark (32 кадри) у режимі Stream */
    /* FIFO_CTRL: Mode = Stream (0b01000000), FTH = 31 (0b00011111) */
    if (sensor_write_reg(dev, REG_FIFO_CTRL, 0x5F) != HAL_OK) return HAL_ERROR;

    /* 2. Прив'язка переривання Watermark до фізичного виводу INT1 */
    if (sensor_write_reg(dev, REG_INT1_CTRL, 0x08) != HAL_OK) return HAL_ERROR;

    /* 3. Увімкнення вимірювань: ODR = 100 Гц, усі 3 осі активні */
    if (sensor_write_reg(dev, REG_CTRL_REG1, 0x57) != HAL_OK) return HAL_ERROR;

    dev->data_ready_flag = false;
    memset(dev->tx_dummy_buffer, 0x00, sizeof(dev->tx_dummy_buffer));
    /* Перший байт передачі — адреса початкового регістру з бітами читання та автоінкременту */
    dev->tx_dummy_buffer[0] = REG_FIFO_DATA_OUT | SPI_READ_BIT | SPI_AUTO_INCR_BIT;

    return HAL_OK;
}

/* Викликається з обробника зовнішнього переривання EXTI */
void sensor_on_watermark_isr(SensorFifoDriver *dev) {
    dev->data_ready_flag = true;
}

bool sensor_fetch_fifo_burst(SensorFifoDriver *dev) {
    if (!dev->data_ready_flag) return false;

    uint8_t fifo_status = 0;
    if (sensor_read_reg(dev, REG_FIFO_SRC, &fifo_status) != HAL_OK) {
        return false;
    }

    /* Перевірка чи досягнуто порогу Watermark (біт 7) */
    if (!(fifo_status & 0x80)) {
        dev->data_ready_flag = false;
        return false;
    }

    /* Пакетне зчитування 192 байтів через SPI DMA */
    sensor_cs_low(dev);
    HAL_StatusTypeDef status = HAL_SPI_TransmitReceive_DMA(
        dev->hspi,
        dev->tx_dummy_buffer,
        dev->rx_raw_buffer,
        sizeof(dev->rx_raw_buffer)
    );

    if (status != HAL_OK) {
        sensor_cs_high(dev);
        return false;
    }

    return true;
}

void sensor_on_dma_complete(SensorFifoDriver *dev) {
    sensor_cs_high(dev);
    dev->data_ready_flag = false;

    /* Розбір отриманого байтового потоку у масив 16-бітних зразків */
    const uint8_t *raw = &dev->rx_raw_buffer[1]; /* Пропускаємо dummy-байт адреси */
    for (size_t i = 0; i < SENSOR_FIFO_WATERMARK; ++i) {
        size_t offset = i * SENSOR_FRAME_SIZE;
        dev->parsed_samples[i].x = (int16_t)((uint16_t)raw[offset + 0] | ((uint16_t)raw[offset + 1] << 8));
        dev->parsed_samples[i].y = (int16_t)((uint16_t)raw[offset + 2] | ((uint16_t)raw[offset + 3] << 8));
        dev->parsed_samples[i].z = (int16_t)((uint16_t)raw[offset + 4] | ((uint16_t)raw[offset + 5] << 8));
    }
}
