#include "driver/sdmmc_host.h"
#include "esp_vfs_fat.h"
#include "esp_camera.h"

// Налаштування SDMMC у 1-бітному режимі для вивільнення GPIO4, GPIO12, GPIO13
esp_err_t init_sd_card_1bit(void) {
    sdmmc_host_t host = SDMMC_HOST_DEFAULT();
    host.flags = SDMMC_HOST_FLAG_1BIT; // Вмикаємо 1-бітну шину

    sdmmc_slot_config_t slot_config = SDMMC_SLOT_CONFIG_DEFAULT();
    slot_config.width = 1; // Задіємо лише лінію D0 (GPIO2)

    esp_vfs_fat_sdmmc_mount_config_t mount_config = {
        .format_if_mount_failed = false,
        .max_files = 5,
        .allocation_unit_size = 16 * 1024
    };

    sdmmc_card_t* card;
    return esp_vfs_fat_sdmmc_mount("/sdcard", &host, &slot_config, &mount_config, &card);
}
