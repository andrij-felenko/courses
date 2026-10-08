#include "esp_err.h"
#include <stdint.h>

typedef enum {
    OV2640_FMT_RAW = 0,
    OV2640_FMT_YUV422,
    OV2640_FMT_RGB565,
    OV2640_FMT_JPEG
} ov2640_format_t;

typedef enum {
    OV2640_RES_UXGA = 0,  // 1600x1200
    OV2640_RES_SVGA,      // 800x600
    OV2640_RES_VGA        // 640x480
} ov2640_res_t;

// Прототип безпечного запису в реєстр
esp_err_t ov2640_write_register_safe(uint8_t bank, uint8_t reg, uint8_t val);

// Налаштування вихідного формату в Bank 1
esp_err_t ov2640_set_output_format(ov2640_format_t fmt) {
    esp_err_t err = ESP_OK;
    switch (fmt) {
        case OV2640_FMT_JPEG:
            // Ввімкнення апаратного JPEG-модуля та форматування DSP
            err |= ov2640_write_register_safe(1, 0xDA, 0x10); // IMAGE_MODE: JPEG enable
            err |= ov2640_write_register_safe(1, 0xE0, 0x00); // RESET: RESET DSP
            err |= ov2640_write_register_safe(1, 0x44, 0x0C); // QS: Quantization Scale
            break;
        case OV2640_FMT_RGB565:
            err |= ov2640_write_register_safe(1, 0xDA, 0x09); // IMAGE_MODE: RGB565 enable
            err |= ov2640_write_register_safe(1, 0xE0, 0x00);
            break;
        case OV2640_FMT_YUV422:
            err |= ov2640_write_register_safe(1, 0xDA, 0x00); // IMAGE_MODE: YUV422 enable
            err |= ov2640_write_register_safe(1, 0xE0, 0x00);
            break;
        default:
            return ESP_ERR_INVALID_ARG;
    }
    return err;
}
