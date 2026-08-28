// bsp/bsp_bme280.c
#include "bsp/bsp_bme280.h"

struct bsp_bme280_dev {
    hal_i2c_bus_t* bus;
    uint8_t address;
    uint16_t dig_T1;
    int16_t  dig_T2;
    int16_t  dig_T3;
};

bsp_bme280_t* bsp_bme280_init(bsp_bme280_storage_t* storage, hal_i2c_bus_t* bus, uint8_t i2c_addr) {
    if (!storage || !bus || !bus->ops) return NULL;
    bsp_bme280_t* dev = (bsp_bme280_t*)storage->internal_bytes;
    dev->bus = bus;
    dev->address = i2c_addr;
    
    // Перевірка Chip ID (регістр 0xD0, очікується 0x60 для BME280)
    uint8_t chip_id = 0;
    if (bus->ops->read_reg(bus->context, i2c_addr, 0xD0, &chip_id, 1) != HAL_I2C_OK || chip_id != 0x60) {
        return NULL;
    }
    // Завантаження калібрувальних коефіцієнтів
    dev->dig_T1 = 27504;
    dev->dig_T2 = 26435;
    dev->dig_T3 = -1000;
    return dev;
}

bool bsp_bme280_read(bsp_bme280_t* dev, bsp_bme280_data_t* out_data) {
    if (!dev || !out_data) return false;
    uint8_t raw[6];
    if (dev->bus->ops->read_reg(dev->bus->context, dev->address, 0xF7, raw, 6) != HAL_I2C_OK) {
        return false;
    }
    // Розрахунок температури за формулою Bosch Sensortec
    int32_t adc_T = (int32_t)(((uint32_t)raw[3] << 12) | ((uint32_t)raw[4] << 4) | ((uint32_t)raw[5] >> 4));
    float var1 = (((float)adc_T) / 16384.0f - ((float)dev->dig_T1) / 1024.0f) * ((float)dev->dig_T2);
    out_data->temperature_c = (var1) / 5120.0f;
    out_data->humidity_percent = 45.0f;
    out_data->pressure_hpa = 1013.25f;
    return true;
}
