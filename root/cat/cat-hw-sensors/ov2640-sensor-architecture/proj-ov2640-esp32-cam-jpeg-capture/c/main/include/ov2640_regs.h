#ifndef OV2640_REGS_H
#define OV2640_REGS_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Адреси банків регістрів */
#define BANK_DSP            0x00
#define BANK_SENSOR         0x01
#define OV2640_BANK_SEL     0xFF

/* Регістри ідентифікації сенсора (Bank 0x01 Sensor) */
#define OV2640_REG_PID      0x0A    /**< Product ID MSB (Очікується 0x26) */
#define OV2640_REG_VER      0x0B    /**< Product ID LSB (Очікується 0x42) */
#define OV2640_REG_MIDH     0x1C    /**< Manufacturer ID High (0x7F) */
#define OV2640_REG_MIDL     0x1D    /**< Manufacturer ID Low (0xA2) */
#define OV2640_REG_CLKRC    0x11    /**< Internal Clock Divider */
#define OV2640_REG_COM7     0x12    /**< Reset / Format Control */
#define OV2640_REG_COM10    0x15    /**< Output drive & PCLK polarity */

/* Регістри налаштування DSP та компресора (Bank 0x00 DSP) */
#define OV2640_REG_R_BYPASS 0x05    /**< DSP Bypass Control */
#define OV2640_REG_QS       0x44    /**< JPEG Quality Scale Coefficient (1..63) */
#define OV2640_REG_CTRL0    0x2A    /**< DSP Control 0 */
#define OV2640_REG_ZMOW     0x51    /**< Zoom Out Width */
#define OV2640_REG_ZMOH     0x52    /**< Zoom Out Height */
#define OV2640_REG_ZMOH_W   0x53    /**< Zoom Out Height/Width MSB */
#define OV2640_REG_IMAGE_MODE 0xDA  /**< Image Format Selection (JPEG/YUV/RGB) */
#define OV2640_REG_RESET    0xE0    /**< Software Reset DSP */

/* Маска системного скидання */
#define COM7_RESET          0x80

/**
 * @brief Структура пара регістр-значення для пакетного вивантаження конфігурації.
 */
typedef struct {
    uint8_t reg;
    uint8_t val;
} ov2640_reg_val_t;

/* Таблиця програмного скидання */
static const ov2640_reg_val_t ov2640_reset_regs[] = {
    {OV2640_BANK_SEL, BANK_SENSOR},
    {OV2640_REG_COM7, COM7_RESET},
    {0xFF, 0xFF}
};

/* Базова конфігурація матриці та підсилювача (Sensor Bank 0x01) */
static const ov2640_reg_val_t ov2640_sensor_init_regs[] = {
    {OV2640_BANK_SEL, BANK_SENSOR},
    {0x12, 0x80}, /* Reset */
    {0x11, 0x01}, /* CLKRC internal prescaler */
    {0x2a, 0x00},
    {0x2b, 0x00},
    {0x12, 0x00}, /* SVGA, YUV422 */
    {0x0c, 0x00},
    {0x0d, 0x00},
    {0x0e, 0x00},
    {0x13, 0xe0}, /* AEC, AGC, AWB enable */
    {0x14, 0x48}, /* AGC ceiling 8x */
    {0x22, 0x00},
    {0x23, 0x00},
    {0x28, 0x00},
    {0x42, 0x00},
    {0x4b, 0x09},
    {0x18, 0xc8},
    {0x19, 0x96},
    {0x1a, 0x00},
    {0x32, 0x36},
    {0x37, 0x40},
    {0x4f, 0xca},
    {0x50, 0xa8},
    {0x5a, 0x23},
    {0x6d, 0x00},
    {0x3d, 0x38},
    {0x39, 0x12},
    {0x35, 0xda},
    {0x22, 0x10},
    {0x37, 0x40},
    {0x23, 0x00},
    {0x3a, 0x07},
    {0x3c, 0x20},
    {0x3d, 0x38},
    {0x06, 0x02},
    {0x07, 0xc0},
    {0x0d, 0x00},
    {0x0e, 0x00},
    {0x4c, 0x00},
    {0xFF, 0xFF}
};

/* Налаштування цифрового сигнального процесора (DSP Bank 0x00) */
static const ov2640_reg_val_t ov2640_dsp_init_regs[] = {
    {OV2640_BANK_SEL, BANK_DSP},
    {0x2c, 0x0c},
    {0x2e, 0xdf},
    {0x3e, 0x00},
    {0x51, 0x80},
    {0x52, 0x60},
    {0x53, 0x00},
    {0x55, 0x00},
    {0x57, 0x00},
    {0x5a, 0x80},
    {0x5b, 0x60},
    {0x5c, 0x00},
    {0xd3, 0x04},
    {0xe0, 0x04},
    {0xda, 0x10}, /* Enable JPEG output mode */
    {0xe1, 0x67},
    {0xe5, 0x05},
    {0xf0, 0x00},
    {0xf1, 0x00},
    {0xf2, 0x00},
    {0xf3, 0x00},
    {0xf4, 0x00},
    {0xf5, 0x00},
    {0xf6, 0x00},
    {0xf7, 0x00},
    {0xf8, 0x00},
    {0xf9, 0x00},
    {0xfa, 0x00},
    {0xFF, 0xFF}
};

/* Конфігурація для виходу JPEG */
static const ov2640_reg_val_t ov2640_jpeg_init_regs[] = {
    {OV2640_BANK_SEL, BANK_DSP},
    {OV2640_REG_R_BYPASS, 0x00}, /* DSP активний */
    {OV2640_REG_IMAGE_MODE, 0x10}, /* JPEG Mode */
    {0xe0, 0x04},
    {0xd7, 0x03},
    {0xd9, 0x10},
    {0xe1, 0x67},
    {0xe5, 0x05},
    {OV2640_REG_QS, 0x0C}, /* Якість компресії за замовчуванням */
    {0xFF, 0xFF}
};

/* Таблиця конфігурації роздільності SVGA (800x600) у форматі JPEG */
static const ov2640_reg_val_t ov2640_svga_jpeg_regs[] = {
    {OV2640_BANK_SEL, BANK_DSP},
    {0x51, 0x64}, /* ZMOW (Zoom out width offset) */
    {0x52, 0x4B}, /* ZMOH (Zoom out height offset) */
    {0x53, 0x00},
    {0x54, 0x00},
    {0x55, 0x00},
    {0x57, 0x00},
    {0x5A, 0x64}, /* Output width 800 (0x64 * 8) */
    {0x5B, 0x4B}, /* Output height 600 (0x4B * 8) */
    {0x5C, 0x00},
    {0xE0, 0x04},
    {0xDA, 0x10},
    {0xFF, 0xFF}
};

/* Таблиця конфігурації роздільності UXGA (1600x1200) у форматі JPEG */
static const ov2640_reg_val_t ov2640_uxga_jpeg_regs[] = {
    {OV2640_BANK_SEL, BANK_DSP},
    {0x51, 0xC8},
    {0x52, 0x96},
    {0x53, 0x00},
    {0x54, 0x00},
    {0x55, 0x00},
    {0x57, 0x00},
    {0x5A, 0xC8}, /* Output width 1600 (0xC8 * 8) */
    {0x5B, 0x96}, /* Output height 1200 (0x96 * 8) */
    {0x5C, 0x00},
    {0xE0, 0x04},
    {0xDA, 0x10},
    {0xFF, 0xFF}
};

/* Таблиця конфігурації роздільності CIF (352x288) у форматі JPEG */
static const ov2640_reg_val_t ov2640_cif_jpeg_regs[] = {
    {OV2640_BANK_SEL, BANK_DSP},
    {0x51, 0x2C},
    {0x52, 0x24},
    {0x53, 0x00},
    {0x54, 0x00},
    {0x55, 0x00},
    {0x57, 0x00},
    {0x5A, 0x2C}, /* Output width 352 (0x2C * 8) */
    {0x5B, 0x24}, /* Output height 288 (0x24 * 8) */
    {0x5C, 0x00},
    {0xE0, 0x04},
    {0xDA, 0x10},
    {0xFF, 0xFF}
};

#ifdef __cplusplus
}
#endif

#endif /* OV2640_REGS_H */
