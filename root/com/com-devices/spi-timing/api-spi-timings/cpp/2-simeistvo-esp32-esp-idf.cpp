#include "driver/spi_master.h"
#include <memory>
#include <expected>

class EspSpiDevice {
public:
    enum class Error { AddDeviceFailed };

    static std::expected<EspSpiDevice, Error> create(spi_host_device_t host, int csPin, int freqHz, int inputDelayNs) {
        spi_device_interface_config_t devcfg{};
        devcfg.command_bits = 8;
        devcfg.address_bits = 24;
        devcfg.dummy_bits = 8;
        devcfg.mode = 0;
        devcfg.clock_speed_hz = freqHz;
        devcfg.input_delay_ns = inputDelayNs;
        devcfg.spics_io_num = csPin;
        devcfg.queue_size = 7;

        spi_device_handle_t handle{nullptr};
        if (spi_bus_add_device(host, &devcfg, &handle) != ESP_OK) {
            return std::unexpected(Error::AddDeviceFailed);
        }
        return EspSpiDevice(handle);
    }

    ~EspSpiDevice() {
        if (handle_) {
            spi_bus_remove_device(handle_);
        }
    }

    EspSpiDevice(const EspSpiDevice&) = delete;
    EspSpiDevice& operator=(const EspSpiDevice&) = delete;
    EspSpiDevice(EspSpiDevice&& o) noexcept : handle_(o.handle_) { o.handle_ = nullptr; }

private:
    explicit EspSpiDevice(spi_device_handle_t h) : handle_(h) {}
    spi_device_handle_t handle_{nullptr};
};
