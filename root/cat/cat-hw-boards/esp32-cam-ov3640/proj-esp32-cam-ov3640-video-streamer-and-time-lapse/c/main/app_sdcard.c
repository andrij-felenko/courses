#include "esp_log.h"
#include "esp_vfs_fat.h"
#include "driver/sdmmc_host.h"
#include <stdio.h>

static const char *TAG = "APP_SDCARD";
#define MOUNT_POINT "/sdcard"

esp_err_t app_sdcard_init(void) {
    esp_vfs_fat_sdmmc_mount_config_t mount_config = {
        .format_if_mount_failed = false,
        .max_files = 5,
        .allocation_unit_size = 16 * 1024
    };

    sdmmc_host_t host = SDMMC_HOST_DEFAULT();
    sdmmc_slot_config_t slot_config = SDMMC_SLOT_CONFIG_DEFAULT();
    slot_config.width = 1; // 1-бітовий режим SDMMC для сумісності камери

    sdmmc_card_t *card;
    esp_err_t ret = esp_vfs_fat_sdmmc_mount(MOUNT_POINT, &host, &slot_config, &mount_config, &card);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Не вдалося змонтувати картку microSD: 0x%x", ret);
        return ret;
    }

    ESP_LOGI(TAG, "Картку microSD успішно змонтовано в %s", MOUNT_POINT);
    return ESP_OK;
}

esp_err_t app_sdcard_save_photo(const uint8_t *data, size_t len, uint32_t photo_num) {
    char filename[64];
    snprintf(filename, sizeof(filename), MOUNT_POINT "/IMG_%04lu.jpg", (unsigned long)photo_num);

    FILE *f = fopen(filename, "wb");
    if (!f) {
        ESP_LOGE(TAG, "Помилка відкриття файла для запису: %s", filename);
        return ESP_FAIL;
    }

    size_t written = fwrite(data, 1, len, f);
    fclose(f);

    if (written != len) {
        ESP_LOGE(TAG, "Записано неповний файл (%zu з %zu байт)", written, len);
        return ESP_FAIL;
    }

    ESP_LOGI(TAG, "Зображення збережено: %s (%zu байт)", filename, len);
    return ESP_OK;
}
