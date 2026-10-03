#include "esp_camera.h"
#include "esp_vfs_fat.h"
#include "sdmmc_cmd.h"

// Налаштування драйвера картки пам'яті у 1-бітовому режимі SDIO
esp_err_t init_sd_card_1bit(void) {
    sdmmc_host_t host = SDMMC_HOST_DEFAULT();
    // Обмеження ширини шини до 1 біта вивільняє GPIO4 та GPIO13
    host.flags = SDMMC_HOST_FLAG_1BIT;

    sdmmc_slot_config_t slot_config = SDMMC_SLOT_CONFIG_DEFAULT();
    slot_config.width = 1;

    esp_vfs_fat_sdmmc_mount_config_t mount_config = {
        .format_if_mount_failed = false,
        .max_files = 5,
        .allocation_unit_size = 16 * 1024
    };

    sdmmc_card_t* card;
    esp_err_t ret = esp_vfs_fat_sdmmc_mount("/sdcard", &host, &slot_config, &mount_config, &card);
    return ret;
}
