#include "nvs_flash.h"
#include "nvs.h"
#include "esp_log.h"
#include <string.h>

static const char* TAG = "nvs_sec_api";

esp_err_t init_encrypted_storage_c(const char* part_label)
{
    nvs_sec_cfg_t cfg;
    const esp_partition_t* key_part = esp_partition_find_first(
        ESP_PARTITION_TYPE_DATA,
        ESP_PARTITION_SUBTYPE_DATA_NVS_KEYS,
        NULL
    );
    if (!key_part) {
        ESP_LOGE(TAG, "Розділ nvs_keys не знайдено у таблиці розділів!");
        return ESP_ERR_NOT_FOUND;
    }

    esp_err_t err = nvs_flash_read_security_cfg(key_part, &cfg);
    if (err == ESP_ERR_NVS_KEYS_NOT_INITIALIZED) {
        ESP_LOGW(TAG, "Ключі відсутні (перший старт). Генеруємо нову конфігурацію...");
        err = nvs_flash_generate_keys(key_part, &cfg);
    }
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося отримати ключі шифрування: 0x%x", err);
        return err;
    }

    err = nvs_flash_secure_init_partition(part_label, &cfg);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка монтування зашифрованого розділу %s: 0x%x", part_label, err);
    }

    // Очищення структури ключів у RAM
    explicit_bzero(&cfg, sizeof(cfg));
    return err;
}
