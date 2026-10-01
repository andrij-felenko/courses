#include "esp_camera.h"

static camera_config_t camera_config = {
    .pin_pwdn     = GPIO_NUM_32,
    .pin_reset    = -1,
    .pin_xclk     = GPIO_NUM_0,
    .pin_sscb_sda = GPIO_NUM_26,
    .pin_sscb_scl = GPIO_NUM_27,

    .pin_d7       = GPIO_NUM_35,
    .pin_d6       = GPIO_NUM_34,
    .pin_d5       = GPIO_NUM_39,
    .pin_d4       = GPIO_NUM_36,
    .pin_d3       = GPIO_NUM_21,
    .pin_d2       = GPIO_NUM_19,
    .pin_d1       = GPIO_NUM_18,
    .pin_d0       = GPIO_NUM_5,
    .pin_vsync    = GPIO_NUM_25,
    .pin_href     = GPIO_NUM_23,
    .pin_pclk     = GPIO_NUM_22,

    .xclk_freq_hz = 20000000,
    .ledc_timer   = LEDC_TIMER_0,
    .ledc_channel = LEDC_CHANNEL_0,

    .pixel_format = PIXFORMAT_JPEG,
    .frame_size   = FRAMESIZE_UXGA,

    .jpeg_quality = 12,
    .fb_count     = 2,
    .grab_mode    = CAMERA_GRAB_LATEST,
    .fb_location  = CAMERA_FB_IN_PSRAM
};
