#include "driver/spi_master.h"
#include <stdexcept>

class EspSpiDevice {
public:
    EspSpiDevice(spi_host_device_t host, int cs_pin, int mode, int speed_hz) {
        spi_device_interface_config_t devcfg{};
        devcfg.clock_speed_hz = speed_hz;
        devcfg.mode = static_cast<uint8_t>(mode); // Вибір режиму 0..3
        devcfg.spics_io_num = cs_pin;
        devcfg.queue_size = 1;

        if (spi_bus_add_device(host, &devcfg, &handle_) != ESP_OK) {
            throw std::runtime_error("Не вдалося додати пристрій SPI до шини");
        }
    }

    ~EspSpiDevice() {
        if (handle_) {
            spi_bus_remove_device(handle_);
        }
    }

    spi_device_handle_t get() const noexcept { return handle_; }

private:
    spi_device_handle_t handle_{nullptr};
};
