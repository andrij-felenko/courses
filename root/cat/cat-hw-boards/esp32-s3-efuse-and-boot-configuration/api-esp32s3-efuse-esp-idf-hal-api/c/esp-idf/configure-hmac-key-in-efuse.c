#include "esp_log.h"
#include "esp_efuse.h"
#include "esp_efuse_table.h"

static const char *TAG = "security_mgr";

esp_err_t configure_hmac_key_in_efuse(const uint8_t hmac_key[32]) {
    size_t secure_boot_bit_cnt = 0;

    // Перевірка стану системи Secure Boot
    esp_err_t err = esp_efuse_read_field_cnt(ESP_EFUSE_SECURE_BOOT_EN, &secure_boot_bit_cnt);
    if (err == ESP_OK) {
        ESP_LOGI(TAG, "Secure Boot %s", (secure_boot_bit_cnt > 0) ? "активовано" : "не використовується");
    }

    // Програмування 256-бітного ключа HMAC у блок EFUSE_BLK4
    // Автоматично записує KEY_PURPOSE та випалює маску read-disable
    err = esp_efuse_write_key(EFUSE_BLK4,
                             ESP_EFUSE_KEY_PURPOSE_HMAC_DOWN_ALL,
                             hmac_key,
                             32);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка програмування ключа HMAC у eFuse: %s", esp_err_to_name(err));
        return err;
    }

    ESP_LOGI(TAG, "Ключ HMAC успішно зафіксовано в EFUSE_BLK4 з апаратним захистом!");
    return ESP_OK;
}
