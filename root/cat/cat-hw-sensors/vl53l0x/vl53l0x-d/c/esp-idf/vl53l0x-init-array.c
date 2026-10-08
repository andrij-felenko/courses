#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "driver/i2c.h"
#include "esp_log.h"

#define I2C_MASTER_SCL_IO    22
#define I2C_MASTER_SDA_IO    21
#define I2C_MASTER_NUM       I2C_NUM_0
#define SENSOR_COUNT         2

static const gpio_num_t xshut_pins[SENSOR_COUNT] = {GPIO_NUM_18, GPIO_NUM_19};
static const uint8_t new_addrs[SENSOR_COUNT] = {0x30, 0x31};

void vl53l0x_init_array(void) {
    // Налаштування виводів XSHUT на вихід
    for (int i = 0; i < SENSOR_COUNT; i++) {
        gpio_reset_pin(xshut_pins[i]);
        gpio_set_direction(xshut_pins[i], GPIO_MODE_OUTPUT);
        gpio_set_level(xshut_pins[i], 0); // Переведення в сон
    }
    vTaskDelay(pdMS_TO_TICKS(10));

    // Послідовний підйом XSHUT та програмування регістра 0x8A
    for (int i = 0; i < SENSOR_COUNT; i++) {
        gpio_set_level(xshut_pins[i], 1);
        vTaskDelay(pdMS_TO_TICKS(10));
        
        // Відправка команди зміни адреси по I2C від базової 0x29 до new_addrs[i]
        i2c_cmd_handle_t cmd = i2c_cmd_link_create();
        i2c_master_start(cmd);
        i2c_master_write_byte(cmd, (0x29 << 1) | I2C_MASTER_WRITE, true);
        i2c_master_write_byte(cmd, 0x8A, true); // Регістр I2C_SLAVE__DEVICE_ADDRESS
        i2c_master_write_byte(cmd, new_addrs[i] & 0x7F, true);
        i2c_master_stop(cmd);
        i2c_master_cmd_begin(I2C_MASTER_NUM, cmd, pdMS_TO_TICKS(100));
        i2c_cmd_link_delete(cmd);
    }
}
