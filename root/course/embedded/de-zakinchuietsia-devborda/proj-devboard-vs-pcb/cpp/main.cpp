#include <cstdint>
#include <array>
#include <string_view>
#include <span>
#include <expected>
#include "esp_system.h"
#include "esp_sleep.h"
#include "driver/spi_master.h"
#include "driver/gpio.h"
#include "esp_log.h"
#include "esp_rom_crc.h"

namespace HardwareAudit {

constexpr gpio_num_t PinMiso = GPIO_NUM_19;
constexpr gpio_num_t PinMosi = GPIO_NUM_23;
constexpr gpio_num_t PinClk  = GPIO_NUM_18;
constexpr gpio_num_t PinCs   = GPIO_NUM_5;

constexpr size_t PacketSize = 256;
constexpr uint32_t TestIterations = 10000;
constexpr std::string_view LogTag = "BUS_AUDIT_CPP";

struct BusStats {
    uint32_t totalPackets{0};
    uint32_t crcErrors{0};
    uint32_t timeoutErrors{0};
};

class SpiBusManager {
public:
    explicit SpiBusManager(int clockHz) {
        spi_bus_config_t buscfg{};
        buscfg.miso_io_num = PinMiso;
        buscfg.mosi_io_num = PinMosi;
        buscfg.sclk_io_num = PinClk;
        buscfg.quadwp_io_num = -1;
        buscfg.quadhd_io_num = -1;
        buscfg.max_transfer_sz = PacketSize + 8;

        spi_device_interface_config_t devcfg{};
        devcfg.clock_speed_hz = clockHz;
        devcfg.mode = 0;
        devcfg.spics_io_num = PinCs;
        devcfg.queue_size = 1;
        devcfg.flags = SPI_DEVICE_NO_DUMMY;

        ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST, &buscfg, SPI_DMA_CH_AUTO));
        ESP_ERROR_CHECK(spi_bus_add_device(SPI2_HOST, &devcfg, &handle_));
    }

    ~SpiBusManager() {
        if (handle_) {
            spi_bus_remove_device(handle_);
            spi_bus_free(SPI2_HOST);
        }
    }

    SpiBusManager(const SpiBusManager&) = delete;
    SpiBusManager& operator=(const SpiBusManager&) = delete;

    [[nodiscard]] esp_err_t transfer(std::span<const uint8_t> tx, std::span<uint8_t> rx) noexcept {
        spi_transaction_t t{};
        t.length = tx.size() * 8;
        t.tx_buffer = tx.data();
        t.rx_buffer = rx.data();
        return spi_device_transmit(handle_, &t);
    }

private:
    spi_device_handle_t handle_{nullptr};
};

class DeepSleepManager {
public:
    static void isolatePinsAndSleep(uint64_t durationUs) noexcept {
        gpio_config_t io_conf{};
        io_conf.pin_bit_mask = (1ULL << PinMiso) | (1ULL << PinMosi) |
                               (1ULL << PinClk)  | (1ULL << PinCs);
        io_conf.mode = GPIO_MODE_INPUT;
        io_conf.pull_up_en = GPIO_PULLUP_DISABLE;
        io_conf.pull_down_en = GPIO_PULLDOWN_DISABLE;
        io_conf.intr_type = GPIO_INTR_DISABLE;
        gpio_config(&io_conf);

        ESP_LOGI(LogTag.data(), "Усі піни переведено в Hi-Z стан.");
        esp_sleep_enable_timer_wakeup(durationUs);
        esp_deep_sleep_start();
    }
};

BusStats runStressTest(SpiBusManager& bus) noexcept {
    BusStats stats{};
    std::array<uint8_t, PacketSize> txBuf{};
    std::array<uint8_t, PacketSize> rxBuf{};

    for (uint32_t i = 0; i < TestIterations; ++i) {
        for (size_t b = 0; b < PacketSize - 4; ++b) {
            txBuf[b] = static_cast<uint8_t>(i + b);
        }

        const uint32_t crc = esp_rom_crc32_le(0, txBuf.data(), PacketSize - 4);
        std::memcpy(&txBuf[PacketSize - 4], &crc, sizeof(crc));
        rxBuf.fill(0);

        stats.totalPackets++;
        const esp_err_t err = bus.transfer(txBuf, rxBuf);
        if (err != ESP_OK) {
            stats.timeoutErrors++;
            continue;
        }

        const uint32_t rxCrc = esp_rom_crc32_le(0, rxBuf.data(), PacketSize - 4);
        uint32_t expectedCrc = 0;
        std::memcpy(&expectedCrc, &rxBuf[PacketSize - 4], sizeof(expectedCrc));

        if (rxCrc != expectedCrc || txBuf != rxBuf) {
            stats.crcErrors++;
        }
    }
    return stats;
}

} // namespace HardwareAudit

extern "C" void app_main() {
    ESP_LOGI(HardwareAudit::LogTag.data(), "Запуск C++ тесту шини SPI");

    {
        HardwareAudit::SpiBusManager bus(20000000);
        auto stats = HardwareAudit::runStressTest(bus);
        ESP_LOGI(HardwareAudit::LogTag.data(), "Тест завершено. Всього: %lu, Помилок CRC: %lu",
                 stats.totalPackets, stats.crcErrors);
    } // Деструктор SpiBusManager автоматично звільняє ресурси шини SPI (RAII)

    HardwareAudit::DeepSleepManager::isolatePinsAndSleep(30 * 1000000ULL);
}
