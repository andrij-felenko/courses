#include "driver/i2c.h"
#include "esp_err.h"

class OV2640Controller {
private:
    i2c_port_t m_i2c_port;
    uint8_t m_dev_addr;

public:
    OV2640Controller(i2c_port_t port, uint8_t dev_addr = 0x30) 
        : m_i2c_port(port), m_dev_addr(dev_addr) {}

    esp_err_t write_reg(uint8_t bank, uint8_t reg, uint8_t val) {
        i2c_cmd_handle_t cmd = i2c_cmd_link_create();
        
        // Крок 1: Встановлення банку регістрів (0xFF)
        i2c_master_start(cmd);
        i2c_master_write_byte(cmd, (m_dev_addr << 1) | I2C_MASTER_WRITE, true);
        i2c_master_write_byte(cmd, 0xFF, true);
        i2c_master_write_byte(cmd, bank, true);
        i2c_master_stop(cmd);
        
        esp_err_t ret = i2c_master_cmd_begin(m_i2c_port, cmd, pdMS_TO_TICKS(100));
        i2c_cmd_link_delete(cmd);
        if (ret != ESP_OK) return ret;

        // Крок 2: Запис у потрібний регістр
        cmd = i2c_cmd_link_create();
        i2c_master_start(cmd);
        i2c_master_write_byte(cmd, (m_dev_addr << 1) | I2C_MASTER_WRITE, true);
        i2c_master_write_byte(cmd, reg, true);
        i2c_master_write_byte(cmd, val, true);
        i2c_master_stop(cmd);
        
        ret = i2c_master_cmd_begin(m_i2c_port, cmd, pdMS_TO_TICKS(100));
        i2c_cmd_link_delete(cmd);
        return ret;
    }

    esp_err_t enter_software_standby() {
        // Запис у біт 4 регістра 0x09 (Bank 1)
        return write_reg(1, 0x09, 0x10);
    }
};
