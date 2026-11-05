#include <stdio.h>
#include <stdbool.h>
#include "esp_efuse.h"
#include "esp_efuse_table.h"
#include "esp_log.h"
#include "esp_secure_boot.h"

static const char *TAG = "EFUSE_DIAG_C";

void app_main(void) {
    ESP_LOGI(TAG, "Самодіагностика стану eFuse та апаратного завантаження ESP32-S3");

    // 1. Перевірка, чи активовано Secure Boot під час апаратного завантаження
    bool is_secure_boot_enabled = esp_secure_boot_enabled();
    if (is_secure_boot_enabled) {
        ESP_LOGI(TAG, "[БЕЗПЕКА] Secure Boot v2 УВІМКНЕНО. Образ прошивки верифіковано.");
    } else {
        ESP_LOGW(TAG, "[БЕЗПЕКА] Secure Boot v2 ВИМКНЕНО. Пристрій завантажує будь-який код.");
    }

    // 2. Читання стану JTAG (чи вимкнено він через eFuse)
    bool jtag_disabled = esp_efuse_read_field_bit(ESP_EFUSE_DIS_PAD_JTAG);
    if (jtag_disabled) {
        ESP_LOGI(TAG, "[АПАРАТНИЙ ЗАХИСТ] Інтерфейс JTAG незворотно вимкнено.");
    } else {
        ESP_LOGW(TAG, "[АПАРАТНИЙ ЗАХИСТ] JTAG доступний, можливе відлагодження зловмисником!");
    }

    // 3. Зчитування призначення (KEY_PURPOSE) для системного блоку 4 (KEY0)
    uint8_t purpose = 0;
    esp_err_t err = esp_efuse_read_field_blob(ESP_EFUSE_KEY_PURPOSE_0, &purpose, 4);
    if (err == ESP_OK) {
        ESP_LOGI(TAG, "Призначення ключа в BLOCK4 (KEY_PURPOSE_0): %d", purpose);
    } else {
        ESP_LOGE(TAG, "Помилка читання KEY_PURPOSE для BLOCK4");
    }
}
