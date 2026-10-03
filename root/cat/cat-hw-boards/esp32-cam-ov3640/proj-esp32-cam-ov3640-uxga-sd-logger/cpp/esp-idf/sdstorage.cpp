#include "esp_vfs_fat.h"
#include "driver/sdmmc_host.h"
#include "esp_log.h"
#include <cstdio>

class SDStorage {
private:
    static constexpr const char *TAG = "SD_LOGGER_CPP";
    sdmmc_card_t *card_{nullptr};
    const char *mount_point_{"/sdcard"};

public:
    esp_err_t mount() {
        esp_vfs_fat_sdmmc_mount_config_t mount_config = {
            .format_if_mount_failed = false,
            .max_files = 5,
            .allocation_unit_size = 16 * 1024
        };
        sdmmc_host_t host = SDMMC_HOST_DEFAULT();
        sdmmc_slot_config_t slot_config = SDMMC_SLOT_CONFIG_DEFAULT();
        return esp_vfs_fat_sdmmc_mount(mount_point_, &host, &slot_config, &mount_config, &card_);
    }

    esp_err_t write_file(const char *name, const uint8_t *data, size_t size) {
        char path[64];
        std::snprintf(path, sizeof(path), "%s/%s", mount_point_, name);
        std::FILE *f = std::fopen(path, "wb");
        if (!f) return ESP_FAIL;

        size_t written = std::fwrite(data, 1, size, f);
        std::fflush(f);
        std::fclose(f);
        return (written == size) ? ESP_OK : ESP_FAIL;
    }

    void unmount() {
        if (card_) {
            esp_vfs_fat_sdcard_unmount(mount_point_, card_);
            card_ = nullptr;
        }
    }
};
