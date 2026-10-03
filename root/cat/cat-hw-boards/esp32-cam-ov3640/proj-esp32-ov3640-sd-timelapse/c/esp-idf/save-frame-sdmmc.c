#include "esp_vfs_fat.h"
#include "driver/sdmmc_host.h"
#include "esp_camera.h"

static const char *TAG_SD = "sd_store";

esp_err_t save_frame_sdmmc(camera_fb_t *fb, const char *filename) {
    sdmmc_host_t host = SDMMC_HOST_DEFAULT();
    // Налаштування максимальної частоти шини SDMMC 40 МГц
    host.max_freq_khz = SDMMC_FREQ_HIGHSPEED;

    sdmmc_slot_config_t slot_config = SDMMC_SLOT_CONFIG_DEFAULT();
    slot_config.width = 4; // Використання 4-бітної шини даних

    esp_vfs_fat_sdmmc_mount_config_t mount_config = {
        .format_if_mount_failed = false,
        .max_files = 3,
        .allocation_unit_size = 32 * 1024 // Оптимізація під кластери 32 КБ
    };

    sdmmc_card_t *card;
    esp_err_t ret = esp_vfs_fat_sdmmc_mount("/sdcard", &host, &slot_config, &mount_config, &card);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG_SD, "Помилка монтування SDMMC: 0x%x", ret);
        return ret;
    }

    // Відкриття файла на запис у бінарному режимі
    FILE *f = fopen(filename, "wb");
    if (f == NULL) {
        ESP_LOGE(TAG_SD, "Неможливо створити файл на MicroSD");
        esp_vfs_fat_sdcard_unmount("/sdcard", card);
        return ESP_FAIL;
    }

    // Одноразовий прямопотоковий запис всього кадрового буфера через DMA
    size_t written = fwrite(fb->buf, 1, fb->len, f);
    fclose(f);

    // Демонтування карти для скидання внутрішніх кешів контролера MicroSD
    esp_vfs_fat_sdcard_unmount("/sdcard", card);

    if (written != fb->len) {
        ESP_LOGE(TAG_SD, "Записано лише %d з %d байт", written, fb->len);
        return ESP_FAIL;
    }

    ESP_LOGI(TAG_SD, "Кадрів успішно збережено: %s (%d байт)", filename, written);
    return ESP_OK;
}
