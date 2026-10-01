#include "esp_vfs_fat.h"
#include "driver/sdmmc_host.h"

// Перехід на 1-бітний режим SDMMC для звільнення GPIO4 (спалаху)
esp_err_t init_sd_card_1bit(void) {
    sdmmc_host_t host = SDMMC_HOST_DEFAULT();
    host.flags = SDMMC_HOST_FLAG_1BIT; // Обов'язковий 1-бітний режим

    sdmmc_slot_config_t slot_config = SDMMC_SLOT_CONFIG_DEFAULT();
    slot_config.width = 1; // Використання лише ліній CMD, CLK та D0 (GPIO2)

    esp_vfs_fat_sdmmc_mount_config_t mount_config = {
        .format_if_mount_failed = false,
        .max_files = 5,
        .allocation_unit_size = 16 * 1024
    };

    sdmmc_card_t *card;
    return esp_vfs_fat_sdmmc_mount("/sdcard", &host, &slot_config, &mount_config, &card);
}
