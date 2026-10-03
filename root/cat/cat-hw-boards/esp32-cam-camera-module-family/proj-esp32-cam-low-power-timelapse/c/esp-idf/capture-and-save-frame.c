#include <stdio.h>
#include <string.h>
#include "esp_sleep.h"
#include "esp_camera.h"
#include "esp_vfs_fat.h"
#include "driver/sdmmc_host.h"
#include "driver/rtc_io.h"
#include "esp_log.h"

#define PWDN_GPIO_NUM     GPIO_NUM_32
#define PIR_GPIO_NUM      GPIO_NUM_13
#define TIME_TO_SLEEP_SEC 600ULL

static const char *TAG = "TIMELAPSE";
static RTC_DATA_ATTR uint32_t boot_count = 0;

static void capture_and_save_frame(void) {
    // Вмикаємо живлення камери через лінію PWDN (низький рівень)
    gpio_set_direction(PWDN_GPIO_NUM, GPIO_MODE_OUTPUT);
    gpio_set_level(PWDN_GPIO_NUM, 0);
    vtaskDelay(pdMS_TO_TICKS(50));

    // Налаштування конфігурації камери OV2640
    camera_config_t config = {
        .ledc_channel = LEDC_CHANNEL_0,
        .ledc_timer = LEDC_TIMER_0,
        .pin_d0 = 5, .pin_d1 = 18, .pin_d2 = 19, .pin_d3 = 21,
        .pin_d4 = 36, .pin_d5 = 39, .pin_d6 = 34, .pin_d7 = 35,
        .pin_xclk = 0, .pin_pclk = 22, .pin_vsync = 25, .pin_href = 23,
        .pin_sscb_sda = 26, .pin_sscb_scl = 27, .pin_pwdn = PWDN_GPIO_NUM,
        .pin_reset = -1, .xclk_freq_hz = 20000000,
        .pixel_format = PIXFORMAT_JPEG,
        .frame_size = FRAMESIZE_UXGA,
        .jpeg_quality = 10,
        .fb_count = 1,
        .grab_mode = CAMERA_GRAB_WHEN_EMPTY
    };

    if (esp_camera_init(&config) != ESP_OK) {
        ESP_LOGE(TAG, "Помилка ініціалізації камери");
        return;
    }

    // Пропускаємо холості кадри для стабілізації експозиції AEC/AGC
    for (int i = 0; i < 2; i++) {
        camera_fb_t *fb_dummy = esp_camera_fb_get();
        if (fb_dummy) esp_camera_fb_return(fb_dummy);
    }

    // Захоплення цільового зображення
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        ESP_LOGE(TAG, "Не вдалося отримати буфер кадру");
        esp_camera_deinit();
        return;
    }

    // Ініціалізація SDMMC у 1-бітовому режимі
    sdmmc_host_t host = SDMMC_HOST_DEFAULT();
    host.flags = SDMMC_HOST_FLAG_1BIT;
    sdmmc_slot_config_t slot_config = SDMMC_SLOT_CONFIG_DEFAULT();
    slot_config.width = 1;

    esp_vfs_fat_sdmmc_mount_config_t mount_config = {
        .format_if_mount_failed = false,
        .max_files = 5,
        .allocation_unit_size = 16 * 1024
    };

    sdmmc_card_t *card;
    if (esp_vfs_fat_sdmmc_mount("/sdcard", &host, &slot_config, &mount_config, &card) == ESP_OK) {
        char filename[32];
        snprintf(filename, sizeof(filename), "/sdcard/img_%04lu.jpg", (unsigned long)boot_count);

        FILE *f = fopen(filename, "wb");
        if (f) {
            fwrite(fb->buf, 1, fb->len, f);
            fflush(f);
            fclose(f);
            ESP_LOGI(TAG, "Кадр збережено: %s", filename);
        }
        esp_vfs_fat_sdcard_unmount("/sdcard", card);
    }

    esp_camera_fb_return(fb);
    esp_camera_deinit();

    // Знеструмлюємо матрицю камери
    gpio_set_level(PWDN_GPIO_NUM, 1);
}

void app_main(void) {
    boot_count++;
    ESP_LOGI(TAG, "Цикл пробудження №%lu", (unsigned long)boot_count);

    capture_and_save_frame();

    // Налаштування джерел пробудження RTC
    esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP_SEC * 1000000ULL);

    rtc_gpio_pullup_dis(PIR_GPIO_NUM);
    rtc_gpio_pulldown_en(PIR_GPIO_NUM);
    esp_sleep_enable_ext0_wakeup(PIR_GPIO_NUM, 1);

    // Ізоляція сигнальних ліній камери та спалаху від паразитних витоків
    rtc_gpio_isolate(GPIO_NUM_4);
    rtc_gpio_isolate(GPIO_NUM_12);

    ESP_LOGI(TAG, "Перехід у режим Deep Sleep на %llu с", TIME_TO_SLEEP_SEC);
    esp_deep_sleep_start();
}
