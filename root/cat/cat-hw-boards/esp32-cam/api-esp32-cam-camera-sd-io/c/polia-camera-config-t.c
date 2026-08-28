#include "esp_camera.h"

static camera_config_t make_camera_config(void) {
    camera_config_t config = {};        // важливо занулити всю структуру

    // канал і таймер LEDC — драйвер ними формує XCLK для сенсора
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer   = LEDC_TIMER_0;

    // вісім ліній даних
    config.pin_d0 = Y2_GPIO_NUM;  config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;  config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;  config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;  config.pin_d7 = Y9_GPIO_NUM;

    // тактові й синхронізація
    config.pin_xclk  = XCLK_GPIO_NUM;
    config.pin_pclk  = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href  = HREF_GPIO_NUM;

    // шина керування сенсором (SCCB ≈ I2C)
    config.pin_sccb_sda = SIOD_GPIO_NUM;
    config.pin_sccb_scl = SIOC_GPIO_NUM;

    config.pin_pwdn  = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;

    config.xclk_freq_hz = 20000000;          // 20 МГц на сенсор
    config.pixel_format = PIXFORMAT_JPEG;    // просимо готовий JPEG, не сирі пікселі

    // Розмір кадру, якість і кількість буферів — залежать від наявності PSRAM.
    if (psramFound()) {
        config.frame_size   = FRAMESIZE_UXGA; // 1600×1200 — на повну
        config.jpeg_quality = 10;             // менше число = краща якість
        config.fb_count     = 2;              // подвійний буфер
        config.fb_location  = CAMERA_FB_IN_PSRAM;
        config.grab_mode    = CAMERA_GRAB_LATEST;
    } else {
        // без PSRAM тягнемо лише скромний кадр в один буфер
        config.frame_size   = FRAMESIZE_SVGA; // 800×600
        config.jpeg_quality = 12;
        config.fb_count     = 1;
        config.fb_location  = CAMERA_FB_IN_DRAM;
        config.grab_mode    = CAMERA_GRAB_WHEN_EMPTY;
    }
    return config;
}
