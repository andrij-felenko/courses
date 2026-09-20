#include "sx1262.h"
#include "driver/spi_master.h"
#include "driver/gpio.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <string.h>

#define PIN_NUM_MISO 13
#define PIN_NUM_MOSI 11
#define PIN_NUM_CLK  12
#define PIN_NUM_CS   10
#define PIN_NUM_BUSY 9

static const char *TAG = "SX1262";
static spi_device_handle_t spi;

static void sx1262_wait_busy(void) {
    while (gpio_get_level(PIN_NUM_BUSY) == 1) {
        vTaskDelay(pdMS_TO_TICKS(1));
    }
}

static void sx1262_write_command(uint8_t cmd, const uint8_t *buf, size_t len) {
    sx1262_wait_busy();
    
    spi_transaction_t t = {
        .length = (1 + len) * 8,
        .tx_data = {cmd},
        .flags = SPI_TRANS_USE_TXDATA
    };
    
    for (size_t i = 0; i < len && i < 3; i++) {
        t.tx_data[i + 1] = buf[i];
    }

    if (len > 3) {
        uint8_t *tx_buf = malloc(1 + len);
        tx_buf[0] = cmd;
        memcpy(&tx_buf[1], buf, len);
        t.tx_buffer = tx_buf;
        t.flags = 0;
        spi_device_polling_transmit(spi, &t);
        free(tx_buf);
    } else {
        spi_device_polling_transmit(spi, &t);
    }
}

bool sx1262_init(void) {
    spi_bus_config_t buscfg = {
        .mosi_io_num = PIN_NUM_MOSI,
        .miso_io_num = PIN_NUM_MISO,
        .sclk_io_num = PIN_NUM_CLK,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
        .max_transfer_sz = 256
    };
    
    spi_device_interface_config_t devcfg = {
        .clock_speed_hz = 1 * 1000 * 1000,
        .mode = 0,
        .spics_io_num = PIN_NUM_CS,
        .queue_size = 7
    };
    
    gpio_set_direction(PIN_NUM_BUSY, GPIO_MODE_INPUT);

    if (spi_bus_initialize(SPI2_HOST, &buscfg, SPI_DMA_CH_AUTO) != ESP_OK) {
        ESP_LOGE(TAG, "Failed to initialize SPI bus");
        return false;
    }
    
    if (spi_bus_add_device(SPI2_HOST, &devcfg, &spi) != ESP_OK) {
        ESP_LOGE(TAG, "Failed to add SPI device");
        return false;
    }
    
    uint8_t stby_config = 0x00; 
    sx1262_write_command(SX1262_CMD_SET_STANDBY, &stby_config, 1);
    
    uint8_t pkt_type = 0x01; // LoRa
    sx1262_write_command(SX1262_CMD_SET_PACKET_TYPE, &pkt_type, 1);

    uint8_t freq_buf[4] = {0x36, 0x40, 0x00, 0x00}; // ~868 MHz
    sx1262_write_command(SX1262_CMD_SET_RF_FREQUENCY, freq_buf, 4);

    ESP_LOGI(TAG, "SX1262 initialized");
    return true;
}

bool sx1262_transmit(const uint8_t *data, uint8_t len) {
    uint8_t base_addr[2] = {0x00, 0x00};
    sx1262_write_command(SX1262_CMD_SET_BUFFER_BASE, base_addr, 2);

    sx1262_wait_busy();
    uint8_t *tx_buf = malloc(1 + 1 + len); 
    tx_buf[0] = SX1262_CMD_WRITE_BUFFER;
    tx_buf[1] = 0x00; 
    memcpy(&tx_buf[2], data, len);
    
    spi_transaction_t t = {
        .length = (1 + 1 + len) * 8,
        .tx_buffer = tx_buf
    };
    spi_device_polling_transmit(spi, &t);
    free(tx_buf);
    
    uint8_t tx_params[3] = {0x00, 0x00, 0x00};
    sx1262_write_command(SX1262_CMD_SET_TX, tx_params, 3);
    
    ESP_LOGI(TAG, "Packet transmitted");
    return true;
}
