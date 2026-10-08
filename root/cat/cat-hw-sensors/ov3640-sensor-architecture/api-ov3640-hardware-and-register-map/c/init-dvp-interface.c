#include <stdint.h>
#include "esp_camera.h"

// Конфігурація периферійного інтерфейсу DVP для захоплення відеопотоку
static camera_config_t dvp_cam_config = {
    .pin_pwdn     = 21,
    .pin_reset    = 22,
    .pin_xclk     = 0,
    .pin_sscb_sda = 26,
    .pin_sscb_scl = 27,

    .pin_d7       = 35,
    .pin_d6       = 34,
    .pin_d5       = 39,
    .pin_d4       = 36,
    .pin_d3       = 19,
    .pin_d2       = 18,
    .pin_d1       = 5,
    .pin_d0       = 4,
    .pin_vsync    = 25,
    .pin_href     = 23,
    .pin_pclk     = 22,

    .xclk_freq_hz = 20000000, // Тактова частота XVCLK = 20 MHz
    .ledc_timer   = LEDC_TIMER_0,
    .ledc_channel = LEDC_CHANNEL_0,

    .pixel_format = PIXFORMAT_RGB565, // 2 байти на піксель
    .frame_size   = FRAMESIZE_QVGA,   // 320x240
    .jpeg_quality = 12,
    .fb_count     = 2                 // Подвійна буферизація DMA
};

esp_err_t init_dvp_interface(void)
{
    // Ініціалізація DVP приймача та виділення DMA буферів
    esp_err_t err = esp_camera_init(&dvp_cam_config);
    if (err != ESP_OK) {
        return err;
    }
    return ESP_OK;
}
