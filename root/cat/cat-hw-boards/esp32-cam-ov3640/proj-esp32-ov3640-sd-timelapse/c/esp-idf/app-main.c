#include <stdio.h>
#include "esp_sleep.h"
#include "esp_log.h"
#include "esp_camera.h"

// Змінна зберігається в пам'яті RTC і не скидається при deep sleep
static RTC_DATA_ATTR uint32_t boot_count = 0;
#define TIME_TO_SLEEP_SEC 60 // Інтервал між знімками: 60 секунд

void app_main(void) {
    boot_count++;
    ESP_LOGI("TIMELAPSE", "Пробудження № %d", boot_count);

    // 1. Ініціалізація OV3640 у режимі UXGA
    if (init_ov3640_uxga() == ESP_OK) {
        // 2. Отримання кадрового буфера
        camera_fb_t *fb = esp_camera_fb_get();
        if (fb) {
            char filename[64];
            snprintf(filename, sizeof(filename), "/sdcard/img_%05d.jpg", boot_count);

            // 3. Збереження кадру на MicroSD через SDMMC 4-bit
            save_frame_sdmmc(fb, filename);

            // Повернення буфера камери
            esp_camera_fb_return(fb);
        }
        // Деініціалізація камери для вимкнення XCLK
        esp_camera_deinit();
    }

    // 4. Налаштування таймера RTC на 60 секунд
    esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP_SEC * 1000000ULL);
    ESP_LOGI("TIMELAPSE", "Перехід у deep sleep на %d сек...", TIME_TO_SLEEP_SEC);

    // 5. Перехід у режим глибокого сну
    esp_deep_sleep_start();
}
