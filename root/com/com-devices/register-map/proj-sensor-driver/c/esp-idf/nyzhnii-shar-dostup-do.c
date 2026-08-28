#include "driver/i2c.h"
#include "esp_log.h"

#define I2C_PORT     I2C_NUM_0
#define MPU_ADDR     0x68
#define REG_WHO      0x75
#define REG_PWR      0x6B
#define REG_CFG      0x1C
#define REG_XOUT_H   0x3B
#define MPU_OK       ESP_OK
#define MPU_WAIT     pdMS_TO_TICKS(100)   // стеля очікування обміну

static const char *TAG = "mpu";

// записати один байт val у регістр reg; повертає esp_err_t (ESP_OK — успіх)
static esp_err_t mpu_write(uint8_t reg, uint8_t val) {
    uint8_t tx[2] = { reg, val };            // номер регістра + дані одним обміном
    return i2c_master_write_to_device(I2C_PORT, MPU_ADDR, tx, 2, MPU_WAIT);
}

// прочитати n байтів поспіль від reg у buf; повертає esp_err_t
static esp_err_t mpu_read(uint8_t reg, uint8_t *buf, size_t n) {
    // write_read сам ставить повторний старт між номером регістра й читанням
    esp_err_t err = i2c_master_write_read_device(I2C_PORT, MPU_ADDR,
                                                 &reg, 1, buf, n, MPU_WAIT);
    if (err != ESP_OK) ESP_LOGE(TAG, "reg 0x%02X: %s", reg, esp_err_to_name(err));
    return err;
}
