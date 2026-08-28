#include "stm32f4xx_hal.h"
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#define IMU_SPI_HANDLE       hspi1
#define IMU_FRAME_SIZE       15
#define IMU_READ_BURST_CMD   0x80 | 0x20

extern SPI_HandleTypeDef IMU_SPI_HANDLE;

static uint8_t g_spi_tx_buf[IMU_FRAME_SIZE] __attribute__((aligned(4)));
static uint8_t g_spi_rx_buf[2][IMU_FRAME_SIZE] __attribute__((aligned(4)));

static volatile uint8_t g_active_rx_buf_idx = 0;
static volatile bool    g_imu_data_ready_flag = false;

void imu_dma_init(void) {
    memset(g_spi_tx_buf, 0x00, IMU_FRAME_SIZE);
    g_spi_tx_buf[0] = IMU_READ_BURST_CMD;
}

void imu_trigger_burst_read(void) {
    HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_RESET);
    uint8_t rx_idx = g_active_rx_buf_idx;
    HAL_SPI_TransmitReceive_DMA(&IMU_SPI_HANDLE, g_spi_tx_buf, g_spi_rx_buf[rx_idx], IMU_FRAME_SIZE);
}

void HAL_SPI_TxRxCpltCallback(SPI_HandleTypeDef *hspi) {
    if (hspi->Instance == SPI1) {
        HAL_GPIO_WritePin(GPIOA, GPIO_PIN_4, GPIO_PIN_SET);
        g_active_rx_buf_idx ^= 1;
        __DMB(); /* Апаратний бар'єр пам'яті для синхронізації ядер */
        g_imu_data_ready_flag = true;
    }
}
