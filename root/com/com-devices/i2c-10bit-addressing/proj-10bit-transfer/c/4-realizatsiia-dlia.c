#include "driver/i2c_master.h"
#include "esp_err.h"

/* Конфігурація та додавання 10-бітного веденого пристрою на шину */
esp_err_t esp32_add_10bit_device(i2c_master_bus_handle_t bus_handle, uint16_t addr10, i2c_master_dev_handle_t *dev_handle) {
    i2c_device_config_t dev_cfg = {
        .dev_addr_length = I2C_ADDR_BIT_LEN_10, /* 10-бітна адресація */
        .device_address  = addr10,
        .scl_speed_hz    = 100000,              /* 100 кГц */
    };
    return i2c_master_bus_add_device(bus_handle, &dev_cfg, dev_handle);
}

/* Читання масиву даних із 10-бітного пристрою */
esp_err_t esp32_10bit_read_reg(i2c_master_dev_handle_t dev_handle, uint8_t reg_addr, uint8_t *buf, size_t len) {
    /* i2c_master_transmit_receive виконує START -> Запис регістра -> Repeated START -> Читання -> STOP */
    return i2c_master_transmit_receive(dev_handle, &reg_addr, 1, buf, len, 1000);
}
