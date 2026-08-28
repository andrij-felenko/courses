#include <stdio.h>
#include <string.h>
#include "esp_log.h"
#include "nvs_flash.h"
#include "nvs.h"

static const char* TAG = "nvs_sec_demo";

esp_err_t initialize_and_save_secret_c(const char* token)
{
    // 1. Пошук розділу ключів nvs_keys
    const esp_partition_t* key_part = esp_partition_find_first(
        ESP_PARTITION_TYPE_DATA,
        ESP_PARTITION_SUBTYPE_DATA_NVS_KEYS,
        NULL
    );
    if (key_part == NULL) {
        ESP_LOGE(TAG, "Розділ nvs_keys не знайдено в таблиці розділів!");
        return ESP_ERR_NOT_FOUND;
    }

    // 2. Зчитування ключів безпеки
    nvs_sec_cfg_t cfg;
    esp_err_t err = nvs_flash_read_security_cfg(key_part, &cfg);
    if (err == ESP_ERR_NVS_KEYS_NOT_INITIALIZED) {
        ESP_LOGW(TAG, "Ключі NVS відсутні. Генеруємо новий 64-байтовий ключ...");
        err = nvs_flash_generate_keys(key_part, &cfg);
    }
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося отримати ключі безпеки: 0x%x", err);
        return err;
    }

    // 3. Ініціалізація зашифрованого NVS за замовчуванням
    err = nvs_flash_secure_init(&cfg);
    if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_WRONG_ENCRYPTION) {
        ESP_LOGE(TAG, "Помилка сховища NVS. Потрібне стирання розділу.");
        return err;
    }

    // 4. Безпечне відкриття простору імен "auth"
    nvs_handle_t nvs_handle;
    err = nvs_open("auth", NVS_READWRITE, &nvs_handle);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка відкриття простору NVS: 0x%x", err);
        explicit_bzero(&cfg, sizeof(cfg));
        return err;
    }

    // 5. Запис конфіденційного токена та фіксація у Flash
    err = nvs_set_str(nvs_handle, "api_token", token);
    if (err == ESP_OK) {
        err = nvs_commit(nvs_handle);
        ESP_LOGI(TAG, "Секретний токен успішно зашифровано й збережено");
    }

    nvs_close(nvs_handle);

    // 6. Критично: обов'язкове очищення ключів у RAM
    explicit_bzero(&cfg, sizeof(cfg));
    return err;
}
