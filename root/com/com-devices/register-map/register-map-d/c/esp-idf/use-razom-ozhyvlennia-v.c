#include "driver/i2c.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"

static const char *TAG = "mpu6050";

// --- адреси з даташита MPU-6050 ---
#define PORT        I2C_NUM_0       // шина I2C, налаштована через i2c_param_config()
#define ADDR        0x68            // адреса чіпа на шині I2C
#define REG_WHO     0x75            // WHO_AM_I
#define EXPECTED_ID 0x68            // сталий код саме цього чіпа
#define REG_PWR     0x6B            // PWR_MGMT_1
#define REG_CFG     0x1C            // ACCEL_CONFIG (діапазон у бітах 4:3)
#define REG_XOUT_H  0x3B            // старший байт виміру осі X

// прочитати один байт регістра reg
static uint8_t read_reg(uint8_t reg) {
    uint8_t val = 0;
    // драйвер сам робить «запис номера — повторний старт — читання»
    esp_err_t err = i2c_master_write_read_device(PORT, ADDR, &reg, 1,
                                                 &val, 1, pdMS_TO_TICKS(100));
    if (err != ESP_OK) ESP_LOGE(TAG, "читання 0x%02X: %s", reg, esp_err_to_name(err));
    return val;
}

// записати один байт val у регістр reg
static void write_reg(uint8_t reg, uint8_t val) {
    uint8_t buf[2] = { reg, val };   // номер регістра й значення — одним записом
    esp_err_t err = i2c_master_write_to_device(PORT, ADDR, buf, 2, pdMS_TO_TICKS(100));
    if (err != ESP_OK) ESP_LOGE(TAG, "запис 0x%02X: %s", reg, esp_err_to_name(err));
}
