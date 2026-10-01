#include <stdint.h>
#include <esp_err.h>

#define ADXL345_REG_INT_ENABLE   0x2E
#define ADXL345_REG_INT_MAP      0x2F
#define ADXL345_REG_FIFO_CTL     0x38

#define ADXL345_INT_WATERMARK    (1 << 1)
#define ADXL345_FIFO_MODE_STREAM (2 << 6)

extern esp_err_t i2c_write_reg(uint8_t reg, uint8_t value);

// Конфігурація FIFO: режим Stream, поріг Watermark (водяний знак)
esp_err_t adxl345_configure_fifo_stream(uint8_t watermark_samples) {
    uint8_t fifo_ctl_val = ADXL345_FIFO_MODE_STREAM | (watermark_samples & 0x1F);
    
    // 1. Маршрутизуємо переривання Watermark на вивід INT1 (біт = 0 у INT_MAP)
    esp_err_t err = i2c_write_reg(ADXL345_REG_INT_MAP, 0x00);
    if (err != ESP_OK) return err;

    // 2. Дозволяємо переривання Watermark у INT_ENABLE
    err = i2c_write_reg(ADXL345_REG_INT_ENABLE, ADXL345_INT_WATERMARK);
    if (err != ESP_OK) return err;

    // 3. Записуємо режим Stream та поріг заповнення у FIFO_CTL
    return i2c_write_reg(ADXL345_REG_FIFO_CTL, fifo_ctl_val);
}
