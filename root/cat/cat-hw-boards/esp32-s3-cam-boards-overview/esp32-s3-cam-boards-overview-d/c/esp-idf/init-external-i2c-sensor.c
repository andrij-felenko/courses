#include "driver/gpio.h"
#include "driver/i2c.h"

// Налаштування вільних GPIO (GPIO1 та GPIO2) для зовнішнього датчика I2C
// без втручання в шину DVP камери та лінії Octal SPI PSRAM
void init_external_i2c_sensor(void) {
    i2c_config_t i2c_conf = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = GPIO_NUM_1,       // Вільний вивід SDA
        .sda_pullup_en = GPIO_PULLUP_ENABLE,
        .scl_io_num = GPIO_NUM_2,       // Вільний вивід SCL
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .master.clk_speed = 400000,     // Частота шини 400 кГц
    };
    i2c_param_config(I2C_NUM_0, &i2c_conf);
    i2c_driver_install(I2C_NUM_0, i2c_conf.mode, 0, 0, 0);
}
