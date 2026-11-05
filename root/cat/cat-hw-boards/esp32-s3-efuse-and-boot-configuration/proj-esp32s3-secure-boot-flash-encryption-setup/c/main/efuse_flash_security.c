#include "efuse_flash_security.h"
#include "esp_log.h"
#include "esp_efuse.h"
#include "esp_efuse_table.h"
#include "esp_partition.h"
#include <string.h>

static const char *TAG = "EFUSE_SECURITY";

esp_err_t efuse_security_read_status(efuse_security_status_t *status)
{
    if (status == NULL) {
        ESP_LOGE(TAG, "Помилка: надано нулевий вказівник на структуру status");
        return ESP_ERR_INVALID_ARG;
    }

    memset(status, 0, sizeof(efuse_security_status_t));

    /* Отримання стану апаратного шифрування Flash-пам'яті */
    status->flash_encryption_enabled = esp_flash_encryption_enabled();
    status->flash_enc_mode = esp_get_flash_encryption_mode();

    /* Отримання стану перевірки підпису Secure Boot V2 */
    status->secure_boot_enabled = esp_secure_boot_enabled();

    /* Зчитування eFuse-біта блокування апаратного налагодження JTAG */
    size_t bit_cnt = 0;
    esp_err_t err = esp_efuse_read_field_cnt(ESP_EFUSE_DIS_PAD_JTAG, &bit_cnt);
    if (err == ESP_OK && bit_cnt > 0) {
        status->jtag_disabled = true;
    } else {
        status->jtag_disabled = false;
    }

    /* Зчитування eFuse-біта обмеження/вимкнення UART ROM Bootloader */
    bit_cnt = 0;
    err = esp_efuse_read_field_cnt(ESP_EFUSE_DIS_DOWNLOAD_MODE, &bit_cnt);
    if (err == ESP_OK && bit_cnt > 0) {
        status->uart_bootloader_disabled = true;
    } else {
        status->uart_bootloader_disabled = false;
    }

    /* Зчитування eFuse-прапорів захисту від читання та запису ключових блоків (BLOCK_KEY) */
    bit_cnt = 0;
    err = esp_efuse_read_field_cnt(ESP_EFUSE_RD_DIS, &bit_cnt);
    if (err == ESP_OK && bit_cnt > 0) {
        status->key_block_read_protected = true;
    } else {
        status->key_block_read_protected = false;
    }

    bit_cnt = 0;
    err = esp_efuse_read_field_cnt(ESP_EFUSE_WR_DIS, &bit_cnt);
    if (err == ESP_OK && bit_cnt > 0) {
        status->key_block_write_protected = true;
    } else {
        status->key_block_write_protected = false;
    }

    return ESP_OK;
}

void efuse_security_print_summary(const efuse_security_status_t *status)
{
    if (status == NULL) {
        ESP_LOGE(TAG, "Неможливо вивести звіт: status == NULL");
        return;
    }

    ESP_LOGI(TAG, "==================================================");
    ESP_LOGI(TAG, "        ЗВІТ БЕЗПЕКИ АПАРАТНОЇ ПЛАТФОРМИ ESP32-S3");
    ESP_LOGI(TAG, "==================================================");

    if (status->flash_encryption_enabled) {
        if (status->flash_enc_mode == ESP_FLASH_ENC_MODE_RELEASE) {
            ESP_LOGI(TAG, "Flash Encryption : УВІМКНЕНО [Режим RELEASE]");
        } else {
            ESP_LOGW(TAG, "Flash Encryption : УВІМКНЕНО [Режим DEVELOPMENT]");
        }
    } else {
        ESP_LOGE(TAG, "Flash Encryption : ВИМКНЕНО (Дані у Flash не зашифровані!)");
    }

    if (status->secure_boot_enabled) {
        ESP_LOGI(TAG, "Secure Boot V2   : УВІМКНЕНО (Валідацію прошивки підписом RSA/ECDSA активовано)");
    } else {
        ESP_LOGE(TAG, "Secure Boot V2   : ВИМКНЕНО (Завантаження підписаних образів не перевіряється!)");
    }

    if (status->jtag_disabled) {
        ESP_LOGI(TAG, "JTAG Debugging   : ЗАБЛОКОВАНО (Доступ до відлагодження через eFuse закритий)");
    } else {
        ESP_LOGW(TAG, "JTAG Debugging   : ДОЗВОЛЕНО (Ризик несанкціонованого зчитування через JTAG)");
    }

    if (status->uart_bootloader_disabled) {
        ESP_LOGI(TAG, "UART Bootloader  : ОБМЕЖЕНО/ВИМКНЕНО (Режим дампів пам'яті через UART неактивний)");
    } else {
        ESP_LOGW(TAG, "UART Bootloader  : ДОЗВОЛЕНО (UART ROM завантажувач увімкнений)");
    }

    ESP_LOGI(TAG, "eFuse RD_DIS     : %s", status->key_block_read_protected ? "АКТИВНО (Ключі захищені від читання)" : "НЕАКТИВНО");
    ESP_LOGI(TAG, "eFuse WR_DIS     : %s", status->key_block_write_protected ? "АКТИВНО (Ключі захищені від запису)" : "НЕАКТИВНО");
    ESP_LOGI(TAG, "==================================================");
}

esp_err_t efuse_security_write_encrypted_partition(const char *partition_label, size_t offset, const void *data, size_t size)
{
    if (partition_label == NULL || data == NULL || size == 0) {
        ESP_LOGE(TAG, "Помилка аргументів: недопустимий вказівник або нулевий розмір");
        return ESP_ERR_INVALID_ARG;
    }

    /* Перевірка вимоги вирівнювання зсуву та розміру по межі 32 байти для апаратного прискорювача AES-XTS */
    if ((offset % FLASH_ENCRYPTION_BLOCK_SIZE != 0) || (size % FLASH_ENCRYPTION_BLOCK_SIZE != 0)) {
        ESP_LOGE(TAG, "Помилка вирівнювання: зсув (%zu) та розмір (%zu) повинні бути кратними %d байтам",
                 offset, size, FLASH_ENCRYPTION_BLOCK_SIZE);
        return ESP_ERR_INVALID_SIZE;
    }

    const esp_partition_t *partition = esp_partition_find_first(ESP_PARTITION_TYPE_DATA,
                                                                 ESP_PARTITION_SUBTYPE_ANY,
                                                                 partition_label);
    if (partition == NULL) {
        ESP_LOGE(TAG, "Помилка: розділ Flash з міткою '%s' не знайдено", partition_label);
        return ESP_ERR_NOT_FOUND;
    }

    if (offset + size > partition->size) {
        ESP_LOGE(TAG, "Помилка: вихід за межі розділу '%s' (розмір розділу: %zu, запис до: %zu)",
                 partition_label, (size_t)partition->size, offset + size);
        return ESP_ERR_INVALID_SIZE;
    }

    ESP_LOGI(TAG, "Запис %zu байт у розділ '%s' за зсувом 0x%zx через esp_partition_write_raw()...",
             size, partition_label, offset);

    /* Використання esp_partition_write_raw() для безпосереднього запису блоків у зашифрований розділ */
    esp_err_t err = esp_partition_write_raw(partition, offset, data, size);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка запису у Flash розділ '%s': %s (0x%x)",
                 partition_label, esp_err_to_name(err), err);
        return err;
    }

    ESP_LOGI(TAG, "Успішно записано %zu байт у зашифрований розділ '%s'", size, partition_label);
    return ESP_OK;
}

esp_err_t efuse_security_read_encrypted_partition(const char *partition_label, size_t offset, void *buffer, size_t size)
{
    if (partition_label == NULL || buffer == NULL || size == 0) {
        ESP_LOGE(TAG, "Помилка аргументів для зчитування з розділу");
        return ESP_ERR_INVALID_ARG;
    }

    const esp_partition_t *partition = esp_partition_find_first(ESP_PARTITION_TYPE_DATA,
                                                                 ESP_PARTITION_SUBTYPE_ANY,
                                                                 partition_label);
    if (partition == NULL) {
        ESP_LOGE(TAG, "Розділ '%s' для зчитування не знайдено", partition_label);
        return ESP_ERR_NOT_FOUND;
    }

    esp_err_t err = esp_partition_read_raw(partition, offset, buffer, size);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка зчитування з розділу '%s': %s (0x%x)",
                 partition_label, esp_err_to_name(err), err);
        return err;
    }

    return ESP_OK;
}
