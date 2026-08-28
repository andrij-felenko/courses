#include "driver/spi_master.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

static const char *TAG = "rc522";
static spi_device_handle_t rc;

// УВЕСЬ платформозалежний код — оці дві функції. Адреса регістра в SPI-кадрі:
// запис (reg << 1) & 0x7E, читання — той самий байт із піднятим 0x80.
static void pcd_write(uint8_t reg, uint8_t val) {
    uint8_t tx[2] = { (uint8_t)((reg << 1) & 0x7E), val };
    spi_transaction_t t = { .length = 16, .tx_buffer = tx };
    ESP_ERROR_CHECK(spi_device_polling_transmit(rc, &t));
}
static uint8_t pcd_read(uint8_t reg) {
    uint8_t tx[2] = { (uint8_t)(((reg << 1) & 0x7E) | 0x80), 0 }, rx[2];
    spi_transaction_t t = { .length = 16, .tx_buffer = tx, .rx_buffer = rx };
    ESP_ERROR_CHECK(spi_device_polling_transmit(rc, &t));
    return rx[1];
}

void app_main(void) {
    spi_bus_config_t bus = { .miso_io_num = 19, .mosi_io_num = 23, .sclk_io_num = 18,
                             .quadwp_io_num = -1, .quadhd_io_num = -1 };
    ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST, &bus, SPI_DMA_CH_AUTO));
    spi_device_interface_config_t dev = { .clock_speed_hz = 5 * 1000 * 1000, .mode = 0,
                                          .spics_io_num = 5,   // «SDA» плати — це chip-select
                                          .queue_size = 4 };
    ESP_ERROR_CHECK(spi_bus_add_device(SPI2_HOST, &dev, &rc));

    pcd_write(0x01, 0x0F);                        // CommandReg ← SoftReset
    vTaskDelay(pdMS_TO_TICKS(50));
    pcd_write(0x2A, 0x80); pcd_write(0x2B, 0xA9); // таймер очікування відповіді мітки
    pcd_write(0x2C, 0x03); pcd_write(0x2D, 0xE8);
    pcd_write(0x15, 0x40); pcd_write(0x11, 0x3D); // 100% ASK, CRC-preset 0x6363
    pcd_write(0x14, pcd_read(0x14) | 0x03);       // TxControlReg: антена на

    uint8_t uid[10], uid_len, sak;
    while (1) {
        // picc_select — код протоколу ISO 14443A поверх pcd_write/pcd_read.
        // Він однаковий на будь-якому МК; платформа міняє лише транспорт вище.
        if (picc_select(uid, &uid_len, &sak) != ESP_OK) { vTaskDelay(pdMS_TO_TICKS(50)); continue; }
        ESP_LOG_BUFFER_HEX(TAG, uid, uid_len);            // UID: 4 або 7 байтів
        ESP_LOGI(TAG, "Чип: %s", picc_type_name(sak));    // тип із SAK, напр. "MIFARE 1KB"
        picc_halt_a();
    }
}
