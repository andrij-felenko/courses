#include "esp_vfs_fat.h"
#include "driver/sdmmc_host.h"
#include "esp_log.h"
#include <stdio.h>

static const char *TAG = "SD_LOGGER";

esp_err_t save_frame_to_sd(const uint8_t *buffer, size_t len, const char *filename) {
    esp_vfs_fat_sdmmc_mount_config_t mount_config = {
        .format_if_mount_failed = false,
        .max_files = 5,
        .allocation_unit_size = 16 * 1024
    };
    sdmmc_host_t host = SDMMC_HOST_DEFAULT();
    sdmmc_slot_config_t slot_config = SDMMC_SLOT_CONFIG_DEFAULT();
    sdmmc_card_t *card;

    // Монтування файлової системи FATFS через шину SDMMC
    esp_err_t ret = esp_vfs_fat_sdmmc_mount("/sdcard", &host, &slot_config, &mount_config, &card);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка монтування SD-карти: 0x%x", ret);
        return ret;
    }

    char filepath[64];
    snprintf(filepath, sizeof(filepath), "/sdcard/%s", filename);
    FILE *f = fopen(filepath, "wb");
    if (f == NULL) {
        ESP_LOGE(TAG, "Не вдалося відкрити файл для запису");
        esp_vfs_fat_sdcard_unmount("/sdcard", card);
        return ESP_FAIL;
    }

    size_t written = fwrite(buffer, 1, len, f);
    fflush(f);
    fclose(f);

    // Демонтування карти для збереження цілісності FATFS
    esp_vfs_fat_sdcard_unmount("/sdcard", card);

    if (written != len) {
        ESP_LOGE(TAG, "Неповний запис кадру на карту");
        return ESP_FAIL;
    }
    ESP_LOGI(TAG, "Кадрові дані успішно збережено: %s", filepath);
    return ESP_OK;
}
