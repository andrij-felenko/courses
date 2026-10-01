#include <cstdint>
#include "driver/spi_master.h"
#include "driver/gpio.h"
#include "esp_log.h"

class SafeSpiBus {
public:
    static constexpr uint64_t kOctalSpiBlockedMask = 
        (1ULL << 30) | (1ULL << 31) | (1ULL << 32) |
        (1ULL << 33) | (1ULL << 34) | (1ULL << 35) |
        (1ULL << 36) | (1ULL << 37);

    static bool IsGpioBlocked(int gpio_num) {
        if (gpio_num < 0) return false;
        return (kOctalSpiBlockedMask & (1ULL << gpio_num)) != 0;
    }

    static esp_err_t Init(spi_host_device_t host, int mosi, int miso, int sclk, int cs) {
        if (IsGpioBlocked(mosi) || IsGpioBlocked(miso) ||
            IsGpioBlocked(sclk) || IsGpioBlocked(cs)) {
            ESP_LOGE("SafeSpiBus", "Вивід належить до внутрішньої шини Octal SPI!");
            return ESP_ERR_INVALID_ARG;
        }

        spi_bus_config_t buscfg{};
        buscfg.mosi_io_num = mosi;
        buscfg.miso_io_num = miso;
        buscfg.sclk_io_num = sclk;
        buscfg.quadwp_io_num = -1;
        buscfg.quadhd_io_num = -1;
        buscfg.max_transfer_sz = 4092;

        return spi_bus_initialize(host, &buscfg, SPI_DMA_CH_AUTO);
    }
};
