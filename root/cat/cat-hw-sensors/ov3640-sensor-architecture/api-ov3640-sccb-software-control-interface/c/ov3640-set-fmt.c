#include <stdint.h>

typedef enum {
    OV3640_FMT_YUV422 = 0,
    OV3640_FMT_RGB565,
    OV3640_FMT_RAW_RGB,
    OV3640_FMT_JPEG
} ov3640_format_t;

typedef enum {
    OV3640_RES_UXGA = 0,
    OV3640_RES_SVGA,
    OV3640_RES_VGA,
    OV3640_RES_CIF
} ov3640_resolution_t;

int ov3640_set_fmt(ov3640_format_t fmt) {
    uint8_t val = 0;
    switch (fmt) {
        case OV3640_FMT_YUV422:  val = 0x00; break;
        case OV3640_FMT_RGB565:  val = 0x06; break;
        case OV3640_FMT_RAW_RGB: val = 0x01; break;
        case OV3640_FMT_JPEG:    val = 0x10; break;
        default: return -1;
    }
    // Запис у регістр конфігурації формату DSP (наприклад, 0x3602)
    return ov3640_write_reg(OV3640_BANK_DSP, 0x3602, val);
}

int ov3640_set_framesize(ov3640_resolution_t res) {
    int ret = 0;
    switch (res) {
        case OV3640_RES_UXGA:
            ret |= ov3640_write_reg(OV3640_BANK_DSP, 0x3620, 0x00); // Без масштабування
            break;
        case OV3640_RES_VGA:
            ret |= ov3640_write_reg(OV3640_BANK_DSP, 0x3620, 0x04); // Субдискретизація 1/2
            break;
        case OV3640_RES_CIF:
            ret |= ov3640_write_reg(OV3640_BANK_DSP, 0x3620, 0x08); // Субдискретизація 1/4
            break;
        default:
            return -1;
    }
    return ret;
}
