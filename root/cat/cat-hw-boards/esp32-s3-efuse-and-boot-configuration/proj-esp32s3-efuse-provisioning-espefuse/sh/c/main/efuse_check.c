#include <stdio.h>
#include <stdbool.h>
#include "esp_log.h"
#include "esp_efuse.h"
#include "esp_efuse_table.h"
#include "esp_flash_encrypt.h"
#include "esp_secure_boot.h"

static const char *TAG = "efuse_check_c";

void app_main(void) {
    ESP_LOGI(TAG, "Ініціалізація перевірки конфігурації безпеки eFuse...");

    // 1. Перевірка статусу Flash Encryption
    if (esp_flash_encryption_enabled()) {
        ESP_LOGI(TAG, "Flash Encryption: УВІМКНЕНО");
    } else {
        ESP_LOGW(TAG, "Flash Encryption: ВИМКНЕНО");
    }

    // 2. Перевірка статусу Secure Boot
    if (esp_secure_boot_enabled()) {
        ESP_LOGI(TAG, "Secure Boot V2: УВІМКНЕНО");
    } else {
        ESP_LOGW(TAG, "Secure Boot V2: ВИМКНЕНО");
    }

    // 3. Перевірка бітів блокування читання (RD_DIS)
    // На ESP32-S3 ключ Flash Encryption зазвичай лежить у BLOCK_KEY0
    bool key0_rd_dis = esp_efuse_read_field_bit(ESP_EFUSE_RD_DIS_KEY0);
    if (key0_rd_dis) {
        ESP_LOGI(TAG, "BLOCK_KEY0 (Flash Encryption): Читання заблоковано (RD_DIS). Безпечно.");
    } else {
        ESP_LOGE(TAG, "BLOCK_KEY0 (Flash Encryption): Читання ДОЗВОЛЕНО! Ключ може бути скомпрометовано.");
    }

    // 4. Перевірка бітів блокування запису (WR_DIS)
    bool secure_boot_en_wr_dis = esp_efuse_read_field_bit(ESP_EFUSE_WR_DIS_SECURE_BOOT_EN);
    if (secure_boot_en_wr_dis) {
        ESP_LOGI(TAG, "Регістр SECURE_BOOT_EN: Запис заблоковано (WR_DIS). Налаштування захищено.");
    } else {
        ESP_LOGW(TAG, "Регістр SECURE_BOOT_EN: Запис дозволено. Зловмисник може змінити стан.");
    }
}
