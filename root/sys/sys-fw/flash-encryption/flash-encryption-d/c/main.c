#include <stdio.h>
#include <stdbool.h>
#include <string.h>
#include "esp_log.h"
#include "esp_flash_encrypt.h"
#include "esp_partition.h"
#include "esp_efuse.h"
#include "esp_efuse_table.h"

static const char *TAG = "SEC_AUDIT";

void audit_flash_encryption(void)
{
    /* 1. Перевірка загального статусу шифрування */
    bool enc_enabled = esp_flash_encryption_enabled();
    ESP_LOGI(TAG, "Статус Flash Encryption: %s", enc_enabled ? "УВІМКНЕНО" : "ВИМКНЕНО");

    if (!enc_enabled) {
        ESP_LOGW(TAG, "УВАГА: Flash-пам'ять не захищена! Працює відкритий режим.");
        return;
    }

    /* 2. Перевірка режиму: Development чи Release */
    esp_flash_enc_mode_t mode = esp_flash_encryption_get_mode();
    if (mode == ESP_FLASH_ENC_MODE_DEVELOPMENT) {
        ESP_LOGW(TAG, "Режим: DEVELOPMENT (Тестовий). Небезпечно для серійних пристроїв!");
    } else if (mode == ESP_FLASH_ENC_MODE_RELEASE) {
        ESP_LOGI(TAG, "Режим: RELEASE (Виробничий). Апаратні порти заблоковано.");
    }

    /* 3. Демонстрація зчитування розшифрованих та сирих даних */
    const esp_partition_t *part = esp_partition_find_first(
        ESP_PARTITION_TYPE_DATA,
        ESP_PARTITION_SUBTYPE_ANY,
        "storage"
    );

    if (part != NULL && part->encrypted) {
        uint8_t plain_buf[32] = {0};
        uint8_t raw_buf[32] = {0};

        /* Прозоре читання: отримуємо відкритий текст */
        esp_err_t err_plain = esp_partition_read(part, 0, plain_buf, sizeof(plain_buf));

        /* Сире читання: отримуємо криптографічний шифротекст */
        esp_err_t err_raw = esp_partition_read_raw(part, 0, raw_buf, sizeof(raw_buf));

        if (err_plain == ESP_OK && err_raw == ESP_OK) {
            ESP_LOGI(TAG, "Успішно зчитано 32 байти з розділу '%s':", part->label);
            ESP_LOG_BUFFER_HEX_LEVEL("Plaintext (Через MMU)", plain_buf, 32, ESP_LOG_INFO);
            ESP_LOG_BUFFER_HEX_LEVEL("Ciphertext (Фізичний Flash)", raw_buf, 32, ESP_LOG_INFO);

            if (memcmp(plain_buf, raw_buf, 32) != 0) {
                ESP_LOGI(TAG, "Підтверджено: вміст на фізичному носії зашифровано.");
            }
        }
    }
}

esp_err_t write_encrypted_secret(const esp_partition_t *part, size_t offset, const uint8_t *data, size_t len)
{
    /* Запис у зашифрований розділ вимагає строгого вирівнювання на 32 байти */
    if (part == NULL || data == NULL || (len % 32 != 0) || (offset % 32 != 0)) {
        ESP_LOGE(TAG, "Помилка: адреса та довжина запису мусять бути кратними 32 байтам!");
        return ESP_ERR_INVALID_ARG;
    }

    /* Драйвер esp_partition_write автоматично шифрує дані перед записом */
    esp_err_t ret = esp_partition_write(part, offset, data, len);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка запису у Flash: 0x%x", ret);
        return ret;
    }

    ESP_LOGI(TAG, "Успішно зашифровано та збережено %zu байтів за зсувом 0x%zx", len, offset);
    return ESP_OK;
}
