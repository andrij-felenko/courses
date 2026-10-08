#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include "driver/gpio.h"
#include "driver/i2c.h"

#define CDC_I2C_ADDR         0x48
#define CDC_REG_DATA_MSB     0x02
#define CDC_FSR_PF           4.0f
#define CDC_ADC_MAX_CODES    16777215.0f
#define CDC_ADC_ZERO_CODE    8388608.0f

static volatile bool s_data_ready = false;

static void IRAM_ATTR cdc_drdy_isr_handler(void* arg) {
    s_data_ready = true;
}

esp_err_t cdc_read_capacitance(i2c_port_t i2c_num, float *capacitance_pf) {
    if (!s_data_ready) {
        return ESP_ERR_INVALID_STATE;
    }
    s_data_ready = false;

    uint8_t reg = CDC_REG_DATA_MSB;
    uint8_t buffer[3] = {0};

    esp_err_t ret = i2c_master_write_read_device(i2c_num, CDC_I2C_ADDR,
                                                &reg, 1,
                                                buffer, 3,
                                                pdMS_TO_TICKS(50));
    if (ret != ESP_OK) {
        return ret;
    }

    uint32_t raw_code = ((uint32_t)buffer[0] << 16) |
                        ((uint32_t)buffer[1] << 8)  |
                         (uint32_t)buffer[2];

    float code_diff = (float)raw_code - CDC_ADC_ZERO_CODE;
    *capacitance_pf = (code_diff / CDC_ADC_MAX_CODES) * CDC_FSR_PF;

    return ESP_OK;
}
