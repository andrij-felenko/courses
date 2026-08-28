#include "driver/spi_master.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"

static const char *TAG = "rc522";
static spi_device_handle_t rc522;   // додано в шину через spi_bus_add_device()

// Адресний байт MFRC522: біт 7 = 1 читання / 0 запис, біти 6..1 — номер регістра.
static void pcd_write(uint8_t reg, uint8_t v) {
    uint8_t tx[2] = { (uint8_t)((reg << 1) & 0x7E), v };
    spi_transaction_t t = { .length = 16, .tx_buffer = tx };
    ESP_ERROR_CHECK(spi_device_polling_transmit(rc522, &t));
}
static uint8_t pcd_read(uint8_t reg) {
    uint8_t tx[2] = { (uint8_t)(((reg << 1) & 0x7E) | 0x80), 0 }, rx[2];
    spi_transaction_t t = { .length = 16, .tx_buffer = tx, .rx_buffer = rx };
    ESP_ERROR_CHECK(spi_device_polling_transmit(rc522, &t));
    return rx[1];
}

static uint8_t uid[10], uid_len, sak;

void rfid_task(void *arg) {
    pcd_init();                 // SoftReset (0x0F) + увімкнути антену: TxControlReg |= 0x03
    ESP_LOGI(TAG, "Піднесіть мітку...");
    for (;;) {
        // 1. REQA (0x26) — чи озветься нова мітка в полі
        if (picc_request(0x26) != ESP_OK) { vTaskDelay(pdMS_TO_TICKS(50)); continue; }

        // 2. антиколізія й SELECT (0x93) → UID у uid[], відповідь мітки у sak
        if (picc_select(uid, &uid_len, &sak) != ESP_OK) continue;

        // 3. UID
        ESP_LOG_BUFFER_HEX(TAG, uid, uid_len);

        // 4. тип мітки — за SAK: 0x08 Classic 1K, 0x18 Classic 4K, 0x00 Ultralight/NTAG
        ESP_LOGI(TAG, "Тип: %s", picc_type_name(sak));

        // 5. HLTA (0x50 0x00 + CRC) — відпустити мітку, інакше читатимемо її без кінця
        picc_halta();
    }
}
