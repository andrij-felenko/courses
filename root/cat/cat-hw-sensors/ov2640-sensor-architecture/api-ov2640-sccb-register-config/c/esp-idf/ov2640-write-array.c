#include <stdio.h>
#include <stdint.h>
#include "driver/i2c.h"

#define OV2640_SCCB_ADDR 0x30

typedef struct {
    uint8_t reg;
    uint8_t val;
} sensor_reg_t;

static const sensor_reg_t ov2640_init_script[] = {
    {0xFF, 0x01}, // Перемикання на Sensor bank
    {0x12, 0x80}, // Програмний скид (soft reset)
    {0xFF, 0x00}, // Перемикання на DSP bank
    {0x2C, 0xFF}, // Конфігурація вихідних стробів
    {0x2E, 0xDF}, // Налаштування FIFO
    {0x00, 0x00}  // Маркер закінчення таблиці
};

int ov2640_write_array(i2c_port_t i2c_num, const sensor_reg_t *regs) {
    while (regs->reg != 0x00 || regs->val != 0x00) {
        i2c_cmd_handle_t cmd = i2c_cmd_link_create();
        i2c_master_start(cmd);
        i2c_master_write_byte(cmd, OV2640_SCCB_ADDR, true);
        i2c_master_write_byte(cmd, regs->reg, true);
        i2c_master_write_byte(cmd, regs->val, true);
        i2c_master_stop(cmd);
        esp_err_t ret = i2c_master_cmd_begin(i2c_num, cmd, pdMS_TO_TICKS(100));
        i2c_cmd_link_delete(cmd);
        if (ret != ESP_OK) {
            return -1;
        }
        if (regs->reg == 0x12 && regs->val == 0x80) {
            vTaskDelay(pdMS_TO_TICKS(10));
        }
        regs++;
    }
    return 0;
}
