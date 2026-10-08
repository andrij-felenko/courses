// Стійке зчитування даних з обробкою помилок I2C мовою C
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    INA219_OK = 0,
    INA219_ERR_I2C,
    INA219_ERR_TIMEOUT,
    INA219_ERR_OVERFLOW,
    INA219_ERR_NOT_CALIBRATED
} ina219_err_t;

typedef struct {
    float voltage_v;
    float current_a;
    float power_w;
} ina219_data_t;

// Заглушка низькорівневого I2C зчитування з таймаутом
extern int hal_i2c_read_reg16(uint8_t dev_addr, uint8_t reg, uint16_t *val, uint32_t timeout_ms);
extern int hal_i2c_write_reg16(uint8_t dev_addr, uint8_t reg, uint16_t val, uint32_t timeout_ms);

ina219_err_t ina219_read_power_data(uint8_t dev_addr, float current_lsb, float power_lsb, ina219_data_t *out_data) {
    uint16_t bus_raw = 0, current_raw = 0, power_raw = 0;
    int retries = 3;
    
    while (retries-- > 0) {
        if (hal_i2c_read_reg16(dev_addr, 0x02, &bus_raw, 50) == 0) {
            break;
        }
    }
    if (retries < 0) return INA219_ERR_I2C;
    
    // Перевірка математичного переповнення OVF
    if (bus_raw & 0x0001) return INA219_ERR_OVERFLOW;
    
    if (hal_i2c_read_reg16(dev_addr, 0x04, &current_raw, 50) != 0) return INA219_ERR_I2C;
    if (hal_i2c_read_reg16(dev_addr, 0x03, &power_raw, 50) != 0) return INA219_ERR_I2C;
    
    out_data->voltage_v = (float)(bus_raw >> 3) * 0.004f;
    out_data->current_a = (float)((int16_t)current_raw) * current_lsb;
    out_data->power_w = (float)power_raw * power_lsb;
    
    return INA219_OK;
}
