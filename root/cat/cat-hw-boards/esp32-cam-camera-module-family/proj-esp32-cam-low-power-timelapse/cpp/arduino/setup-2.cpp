#include <Arduino.h>
#include "esp_camera.h"
#include "FS.h"
#include "SD_MMC.h"
#include "driver/rtc_io.h"

#define PWDN_GPIO_NUM     32
#define PIR_GPIO_NUM      13
#define TIME_TO_SLEEP_SEC 600ULL

RTC_DATA_ATTR uint32_t boot_count = 0;

void setup() {
    boot_count++;
    Serial.begin(115200);

    pinMode(PWDN_GPIO_NUM, OUTPUT);
    digitalWrite(PWDN_GPIO_NUM, LOW); // Вмикаємо камеру
    delay(50);

    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = 5; config.pin_d1 = 18; config.pin_d2 = 19; config.pin_d3 = 21;
    config.pin_d4 = 36; config.pin_d5 = 39; config.pin_d6 = 34; config.pin_d7 = 35;
    config.pin_xclk = 0; config.pin_pclk = 22; config.pin_vsync = 25; config.pin_href = 23;
    config.pin_sscb_sda = 26; config.pin_sscb_scl = 27; config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = -1; config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;
    config.frame_size = FRAMESIZE_UXGA;
    config.jpeg_quality = 10;
    config.fb_count = 1;
    config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;

    if (esp_camera_init(&config) == ESP_OK) {
        // Пропускаємо кадри для стабілізації AGC/AEC
        for (int i = 0; i < 2; i++) {
            camera_fb_t *fb_dummy = esp_camera_fb_get();
            if (fb_dummy) esp_camera_fb_return(fb_dummy);
        }

        camera_fb_t *fb = esp_camera_fb_get();
        if (fb) {
            // Монтуємо SDMMC у 1-бітовому режимі (mode1p = true)
            if (SD_MMC.begin("/sdcard", true)) {
                String path = "/img_" + String(boot_count) + ".jpg";
                File file = SD_MMC.open(path, FILE_WRITE);
                if (file) {
                    file.write(fb->buf, fb->len);
                    file.flush();
                    file.close();
                }
                SD_MMC.end();
            }
            esp_camera_fb_return(fb);
        }
        esp_camera_deinit();
    }

    digitalWrite(PWDN_GPIO_NUM, HIGH); // Вимикаємо камеру

    // Конфігуруємо таймер RTC та зовнішній PIR-тригер
    esp_sleep_enable_timer_wakeup(TIME_TO_SLEEP_SEC * 1000000ULL);
    rtc_gpio_pullup_dis((gpio_num_t)PIR_GPIO_NUM);
    rtc_gpio_pulldown_en((gpio_num_t)PIR_GPIO_NUM);
    esp_sleep_enable_ext0_wakeup((gpio_num_t)PIR_GPIO_NUM, 1);

    // Ізолюємо лінії від паразитних струмів
    rtc_gpio_isolate(GPIO_NUM_4);
    rtc_gpio_isolate(GPIO_NUM_12);

    esp_deep_sleep_start();
}

void loop() {
    // Код у loop() не виконується
}
