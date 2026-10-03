#include "esp_camera.h"
#include "SD_MMC.h"
#include "esp_sleep.h"

// Лічильник знімків зберігається в RTC пам'яті
RTC_DATA_ATTR uint32_t frame_counter = 0;
#define SLEEP_INTERVAL_SEC 60 // Інтервал таймлапсу в секундах

void setup() {
    Serial.begin(115200);
    frame_counter++;
    Serial.printf("Пробудження таймлапс-камери. Кадр № %u\n", frame_counter);

    // Ініціалізація камери OV3640
    if (setupCameraUXGA()) {
        camera_fb_t *fb = esp_camera_fb_get();
        if (fb) {
            String path = "/pic_" + String(frame_counter) + ".jpg";
            saveFrameToSDMMC(fb, path);
            esp_camera_fb_return(fb);
        }
        esp_camera_deinit(); // Вимкнення генерації XCLK
    }

    // Конфігурація RTC таймера
    esp_sleep_enable_timer_wakeup(SLEEP_INTERVAL_SEC * 1000000ULL);
    Serial.flush();
    
    // Перехід пристрою у режим deep sleep
    esp_deep_sleep_start();
}

void loop() {
    // Код у loop() ніколи не виконується при deep sleep
}
