#include "esp_err.h"
#include "driver/i2c.h"

class Ov3640Diagnostic {
public:
    static constexpr uint8_t SccbAddress = 0x3C;
    static constexpr uint8_t RegBankSelect = 0xFF;
    static constexpr uint8_t RegPidHigh = 0x0A;
    static constexpr uint8_t RegPidLow = 0x0B;

    explicit Ov3640Diagnostic(i2c_port_t port) : i2c_port_(port) {}

    esp_err_t checkIdentity() const {
        if (esp_err_t err = writeRegister(RegBankSelect, 0x01); err != ESP_OK) {
            return err;
        }

        uint8_t high = 0;
        uint8_t low = 0;
        if (esp_err_t err = readRegister(RegPidHigh, high); err != ESP_OK) {
            return err;
        }
        if (esp_err_t err = readRegister(RegPidLow, low); err != ESP_OK) {
            return err;
        }

        return (high == 0x36 && low == 0x48) ? ESP_OK : ESP_ERR_NOT_FOUND;
    }

private:
    i2c_port_t i2c_port_;

    esp_err_t writeRegister(uint8_t reg, uint8_t val) const {
        i2c_cmd_handle_t cmd = i2c_cmd_link_create();
        i2c_master_start(cmd);
        i2c_master_write_byte(cmd, (SccbAddress << 1) | I2C_MASTER_WRITE, true);
        i2c_master_write_byte(cmd, reg, true);
        i2c_master_write_byte(cmd, val, true);
        i2c_master_stop(cmd);
        esp_err_t ret = i2c_master_cmd_begin(i2c_port_, cmd, pdMS_TO_TICKS(100));
        i2c_cmd_link_delete(cmd);
        return ret;
    }

    esp_err_t readRegister(uint8_t reg, uint8_t &val) const {
        i2c_cmd_handle_t cmd = i2c_cmd_link_create();
        i2c_master_start(cmd);
        i2c_master_write_byte(cmd, (SccbAddress << 1) | I2C_MASTER_WRITE, true);
        i2c_master_write_byte(cmd, reg, true);
        i2c_master_start(cmd);
        i2c_master_write_byte(cmd, (SccbAddress << 1) | I2C_MASTER_READ, true);
        i2c_master_read_byte(cmd, &val, I2C_MASTER_NACK);
        i2c_master_stop(cmd);
        esp_err_t ret = i2c_master_cmd_begin(i2c_port_, cmd, pdMS_TO_TICKS(100));
        i2c_cmd_link_delete(cmd);
        return ret;
    }
};
