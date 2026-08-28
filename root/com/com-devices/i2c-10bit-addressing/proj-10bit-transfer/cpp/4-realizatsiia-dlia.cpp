#include "driver/i2c_master.h"
#include "esp_err.h"
#include <span>
#include <cstdint>
#include <expected>

class Esp32I2c10BitDevice {
public:
    Esp32I2c10BitDevice(i2c_master_bus_handle_t bus, uint16_t addr10, uint32_t speed_hz = 100000) {
        i2c_device_config_t dev_cfg{};
        dev_cfg.dev_addr_length = I2C_ADDR_BIT_LEN_10;
        dev_cfg.device_address  = addr10;
        dev_cfg.scl_speed_hz    = speed_hz;

        esp_err_t err = i2c_master_bus_add_device(bus, &dev_cfg, &handle_);
        if (err != ESP_OK) {
            handle_ = nullptr;
        }
    }

    ~Esp32I2c10BitDevice() noexcept {
        if (handle_ != nullptr) {
            i2c_master_bus_rm_device(handle_);
        }
    }

    [[nodiscard]] bool isValid() const noexcept {
        return handle_ != nullptr;
    }

    std::expected<void, esp_err_t> readRegister(
        uint8_t reg_addr,
        std::span<uint8_t> out_buf,
        int timeout_ms = 1000
    ) const noexcept {
        if (!isValid()) {
            return std::unexpected(ESP_ERR_INVALID_STATE);
        }
        esp_err_t err = i2c_master_transmit_receive(
            handle_,
            &reg_addr,
            1,
            out_buf.data(),
            out_buf.size(),
            timeout_ms
        );
        if (err != ESP_OK) {
            return std::unexpected(err);
        }
        return {};
    }

private:
    i2c_master_dev_handle_t handle_{nullptr};
};
