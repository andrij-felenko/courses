#include <stdio.h>
#include "driver/gpio.h"
#include "driver/i2c.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define I2C_PORT_NUM           I2C_NUM_0
#define VL53L0X_DEFAULT_ADDR   0x29
#define VL53L0X_REG_SLAVE_ADDR 0x8A

#define SENSOR_1_XSHUT_GPIO    GPIO_NUM_18
#define SENSOR_2_XSHUT_GPIO    GPIO_NUM_19

esp_err_t vl53l0x_change_address(uint8_t current_addr, uint8_t new_addr) {
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (current_addr << 1) | I2C_MASTER_WRITE, true);
    i2c_master_write_byte(cmd, VL53L0X_REG_SLAVE_ADDR, true);
    i2c_master_write_byte(cmd, new_addr & 0x7F, true);
    i2c_master_stop(cmd);
    esp_err_t ret = i2c_master_cmd_begin(I2C_PORT_NUM, cmd, pdMS_TO_TICKS(100));
    i2c_cmd_link_delete(cmd);
    return ret;
}

void init_multi_sensor_bus(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << SENSOR_1_XSHUT_GPIO) | (1ULL << SENSOR_2_XSHUT_GPIO),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_ENABLE
    };
    gpio_config(&io_conf);

    // Переводимо обидва сенсори у режим скидання
    gpio_set_level(SENSOR_1_XSHUT_GPIO, 0);
    gpio_set_level(SENSOR_2_XSHUT_GPIO, 0);
    vTaskDelay(pdMS_TO_TICKS(10));

    // Запускаємо перший сенсор і призначаємо нову адресу 0x30
    gpio_set_level(SENSOR_1_XSHUT_GPIO, 1);
    vTaskDelay(pdMS_TO_TICKS(5));
    vl53l0x_change_address(VL53L0X_DEFAULT_ADDR, 0x30);

    // Запускаємо другий сенсор і призначаємо нову адресу 0x31
    gpio_set_level(SENSOR_2_XSHUT_GPIO, 1);
    vTaskDelay(pdMS_TO_TICKS(5));
    vl53l0x_change_address(VL53L0X_DEFAULT_ADDR, 0x31);
}
