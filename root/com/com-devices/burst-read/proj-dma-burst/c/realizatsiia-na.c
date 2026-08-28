#include "driver/spi_master.h"
#include "esp_heap_caps.h"
#include <string.h>

#define IMU_HOST        SPI2_HOST
#define IMU_PAYLOAD_LEN 14

static spi_device_handle_t s_spi_dev;
static uint8_t *s_dma_tx_buf = NULL;
static uint8_t *s_dma_rx_buf = NULL;
static spi_transaction_t s_trans;

void imu_esp32_init(void) {
    s_dma_tx_buf = (uint8_t *)heap_caps_malloc(16, MALLOC_CAP_DMA);
    s_dma_rx_buf = (uint8_t *)heap_caps_malloc(16, MALLOC_CAP_DMA);
    memset(s_dma_tx_buf, 0x00, 16);
    s_dma_tx_buf[0] = 0x80 | 0x20;

    memset(&s_trans, 0, sizeof(s_trans));
    s_trans.length    = (1 + IMU_PAYLOAD_LEN) * 8;
    s_trans.tx_buffer = s_dma_tx_buf;
    s_trans.rx_buffer = s_dma_rx_buf;
}
