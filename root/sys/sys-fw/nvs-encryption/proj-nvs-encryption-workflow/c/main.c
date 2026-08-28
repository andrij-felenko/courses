#include <stdio.h>
#include <string.h>
#include "esp_log.h"
#include "nvs_flash.h"
#include "nvs.h"

static const char* TAG = "nvs_workflow";

esp_err_t manage_device_secrets_c(void)
{
    nvs_sec_cfg_t cfg;
    const esp_partition_t* key_part = esp_partition_find_first(
        ESP_PARTITION_TYPE_DATA,
        ESP_PARTITION_SUBTYPE_DATA_NVS_KEYS,
        NULL
    );
    if (!key_part) {
        ESP_LOGE(TAG, "Розділ nvs_keys відсутній у таблиці розділів!");
        return ESP_ERR_NOT_FOUND;
    }

    // Зчитуємо конфігурацію ключів з Flash (прозоре дешифрування через MMU)
    esp_err_t err = nvs_flash_read_security_cfg(key_part, &cfg);
    if (err == ESP_ERR_NVS_KEYS_NOT_INITIALIZED) {
        ESP_LOGW(TAG, "Розділ ключів порожній. Автономна генерація нового ключа...");
        err = nvs_flash_generate_keys(key_part, &cfg);
    }
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Критична помилка конфігурації безпеки: 0x%x", err);
        return err;
    }

    // Ініціалізуємо виділений зашифрований розділ
    err = nvs_flash_secure_init_partition("secret_nvs", &cfg);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося змонтувати secret_nvs: 0x%x", err);
        explicit_bzero(&cfg, sizeof(cfg));
        return err;
    }

    // Відкриваємо простір імен "sec_ns"
    nvs_handle_t handle;
    err = nvs_open_from_partition("secret_nvs", "sec_ns", NVS_READWRITE, &handle);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка відкриття простору імен: 0x%x", err);
        explicit_bzero(&cfg, sizeof(cfg));
        return err;
    }

    // Зчитування приватного ключа клієнта (blob)
    size_t key_len = 0;
    err = nvs_get_blob(handle, "tls_priv_key", NULL, &key_len);
    if (err == ESP_OK && key_len > 0) {
        uint8_t* key_buffer = (uint8_t*)malloc(key_len);
        if (key_buffer) {
            err = nvs_get_blob(handle, "tls_priv_key", key_buffer, &key_len);
            if (err == ESP_OK) {
                ESP_LOGI(TAG, "Приватний ключ TLS успішно прочитано (%zu байтів)", key_len);
            }
            // Гарантоване затирання тимчасового буфера після використання
            explicit_bzero(key_buffer, key_len);
            free(key_buffer);
        }
    } else {
        ESP_LOGW(TAG, "Приватний ключ відсутній. Запис тимчасового токена...");
        const char test_token[] = "DEV_SESSION_TOKEN_998124";
        nvs_set_str(handle, "session_token", test_token);
        nvs_commit(handle);
    }

    // Закриваємо дескриптор сховища
    nvs_close(handle);

    // Обов'язкове затирання криптографічного контексту в стеку
    explicit_bzero(&cfg, sizeof(cfg));
    return ESP_OK;
}
