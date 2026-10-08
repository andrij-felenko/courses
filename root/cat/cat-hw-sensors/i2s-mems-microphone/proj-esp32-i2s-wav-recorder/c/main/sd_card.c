/**
 * @file sd_card.c
 * @brief Реалізація процедур роботи з SD-карткою у середовищі ESP-IDF через VFS FATFS.
 */

#include "sd_card.h"
#include <string.h>
#include "esp_log.h"
#include "driver/sdspi_host.h"
#include "driver/spi_common.h"

static const char *TAG = "SD_CARD";

static sdmmc_card_t *g_sd_card = NULL;
static bool g_is_mounted = false;
static char g_mount_point[32] = SD_CARD_MOUNT_POINT;

esp_err_t sd_card_init(const sd_card_config_t *config)
{
    if (g_is_mounted) {
        ESP_LOGW(TAG, "SD-картка вже примонтована");
        return ESP_OK;
    }

    sd_card_config_t default_cfg = {
        .mount_point = SD_CARD_MOUNT_POINT,
        .pin_miso = SD_CARD_PIN_MISO,
        .pin_mosi = SD_CARD_PIN_MOSI,
        .pin_clk = SD_CARD_PIN_CLK,
        .pin_cs = SD_CARD_PIN_CS,
        .max_files = 5,
        .format_if_mount_failed = 0
    };

    const sd_card_config_t *cfg = (config != NULL) ? config : &default_cfg;
    strncpy(g_mount_point, cfg->mount_point, sizeof(g_mount_point) - 1);

    ESP_LOGI(TAG, "Ініціалізація SD-картки через SPI (MISO=%d, MOSI=%d, CLK=%d, CS=%d)",
             cfg->pin_miso, cfg->pin_mosi, cfg->pin_clk, cfg->pin_cs);

    esp_vfs_fat_sdmmc_mount_config_t mount_config = {
        .format_if_mount_failed = (cfg->format_if_mount_failed != 0),
        .max_files = cfg->max_files,
        .allocation_unit_size = 16 * 1024
    };

    sdmmc_host_t host = SDSPI_HOST_DEFAULT();
    host.slot = SPI2_HOST;

    spi_bus_config_t bus_cfg = {
        .mosi_io_num = cfg->pin_mosi,
        .miso_io_num = cfg->pin_miso,
        .sclk_io_num = cfg->pin_clk,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
        .max_transfer_sz = 4000
    };

    esp_err_t ret = spi_bus_initialize((spi_host_device_t)host.slot, &bus_cfg, SDSPI_DEFAULT_DMA);
    if (ret != ESP_OK && ret != ESP_ERR_INVALID_STATE) {
        ESP_LOGE(TAG, "Не вдалося ініціалізувати шину SPI: %s", esp_err_to_name(ret));
        return ret;
    }

    sdspi_device_config_t slot_config = SDSPI_DEVICE_CONFIG_DEFAULT();
    slot_config.gpio_cs = cfg->pin_cs;
    slot_config.host_id = (spi_host_device_t)host.slot;

    ret = esp_vfs_fat_sdspi_mount(cfg->mount_point, &host, &slot_config, &mount_config, &g_sd_card);
    if (ret != ESP_OK) {
        if (ret == ESP_FAIL) {
            ESP_LOGE(TAG, "Не вдалося змонтувати файлову систему FATFS SD-картки");
        } else {
            ESP_LOGE(TAG, "Помилка ініціалізації SD-картки (%s)", esp_err_to_name(ret));
        }
        spi_bus_free((spi_host_device_t)host.slot);
        return ret;
    }

    g_is_mounted = true;
    ESP_LOGI(TAG, "SD-картка успішно змонтована за шляхом '%s'", cfg->mount_point);
    sdmmc_card_print_info(stdout, g_sd_card);

    return ESP_OK;
}

bool sd_card_is_mounted(void)
{
    return g_is_mounted;
}

esp_err_t sd_card_get_free_space(uint64_t *out_free_bytes, uint64_t *out_total_bytes)
{
    if (!g_is_mounted || g_sd_card == NULL) {
        return ESP_ERR_INVALID_STATE;
    }

    FATFS *fs;
    DWORD fre_clust, fre_sect, tot_sect;

    /* Отримання інформації про кластери FATFS */
    FRESULT res = f_getfree("0:", &fre_clust, &fs);
    if (res != FR_OK) {
        ESP_LOGE(TAG, "Помилка отримання вільного місця FATFS: %d", res);
        return ESP_FAIL;
    }

    tot_sect = (fs->n_fatent - 2) * fs->csize;
    fre_sect = fre_clust * fs->csize;

    if (out_total_bytes != NULL) {
        *out_total_bytes = (uint64_t)tot_sect * 512;
    }
    if (out_free_bytes != NULL) {
        *out_free_bytes = (uint64_t)fre_sect * 512;
    }

    return ESP_OK;
}

esp_err_t sd_card_deinit(void)
{
    if (!g_is_mounted) {
        return ESP_OK;
    }

    esp_err_t ret = esp_vfs_fat_sdcard_unmount(g_mount_point, g_sd_card);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Помилка розмонтування SD-картки: %s", esp_err_to_name(ret));
    } else {
        ESP_LOGI(TAG, "SD-картку розмонтовано");
    }

    spi_bus_free(SPI2_HOST);
    g_sd_card = NULL;
    g_is_mounted = false;

    return ret;
}
