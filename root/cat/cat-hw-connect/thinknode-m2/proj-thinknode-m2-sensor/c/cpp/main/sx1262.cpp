#include "sx1262.hpp"
#include "driver/gpio.h"
#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <vector>
#include <array>

namespace {
    constexpr char TAG[] = "SX1262";
    
    constexpr uint8_t CMD_SET_STANDBY      = 0x80;
    constexpr uint8_t CMD_SET_PACKET_TYPE  = 0x8A;
    constexpr uint8_t CMD_SET_RF_FREQUENCY = 0x86;
    constexpr uint8_t CMD_SET_BUFFER_BASE  = 0x8F;
    constexpr uint8_t CMD_WRITE_BUFFER     = 0x0E;
    constexpr uint8_t CMD_SET_TX           = 0x83;
}

SX1262::SX1262(int miso, int mosi, int clk, int cs, int busy)
    : m_cs(cs), m_busy(busy) {
    
    spi_bus_config_t buscfg = {};
    buscfg.miso_io_num = miso;
    buscfg.mosi_io_num = mosi;
    buscfg.sclk_io_num = clk;
    buscfg.quadwp_io_num = -1;
    buscfg.quadhd_io_num = -1;
    buscfg.max_transfer_sz = 256;

    spi_device_interface_config_t devcfg = {};
    devcfg.clock_speed_hz = 1'000'000;
    devcfg.mode = 0;
    devcfg.spics_io_num = m_cs;
    devcfg.queue_size = 7;

    gpio_set_direction(static_cast<gpio_num_t>(m_busy), GPIO_MODE_INPUT);

    if (spi_bus_initialize(SPI2_HOST, &buscfg, SPI_DMA_CH_AUTO) == ESP_OK) {
        spi_bus_add_device(SPI2_HOST, &devcfg, &m_spi);
    }
}

SX1262::~SX1262() {
    if (m_spi) {
        spi_bus_remove_device(m_spi);
        spi_bus_free(SPI2_HOST);
    }
}

void SX1262::waitBusy() const {
    while (gpio_get_level(static_cast<gpio_num_t>(m_busy)) == 1) {
        vTaskDelay(pdMS_TO_TICKS(1));
    }
}

void SX1262::writeCommand(uint8_t cmd, std::span<const uint8_t> args) {
    if (!m_spi) return;
    waitBusy();
    
    std::vector<uint8_t> tx_buf;
    tx_buf.reserve(1 + args.size());
    tx_buf.push_back(cmd);
    tx_buf.insert(tx_buf.end(), args.begin(), args.end());
    
    spi_transaction_t t = {};
    t.length = tx_buf.size() * 8;
    t.tx_buffer = tx_buf.data();
    
    spi_device_polling_transmit(m_spi, &t);
}

bool SX1262::init() {
    if (!m_spi) return false;

    writeCommand(CMD_SET_STANDBY, std::array<uint8_t, 1>{0x00});
    writeCommand(CMD_SET_PACKET_TYPE, std::array<uint8_t, 1>{0x01});
    writeCommand(CMD_SET_RF_FREQUENCY, std::array<uint8_t, 4>{0x36, 0x40, 0x00, 0x00});

    ESP_LOGI(TAG, "SX1262 initialized");
    return true;
}

bool SX1262::transmit(std::span<const uint8_t> data) {
    if (!m_spi) return false;

    writeCommand(CMD_SET_BUFFER_BASE, std::array<uint8_t, 2>{0x00, 0x00});

    waitBusy();
    std::vector<uint8_t> tx_buf;
    tx_buf.reserve(2 + data.size());
    tx_buf.push_back(CMD_WRITE_BUFFER);
    tx_buf.push_back(0x00);
    tx_buf.insert(tx_buf.end(), data.begin(), data.end());

    spi_transaction_t t = {};
    t.length = tx_buf.size() * 8;
    t.tx_buffer = tx_buf.data();
    spi_device_polling_transmit(m_spi, &t);

    writeCommand(CMD_SET_TX, std::array<uint8_t, 3>{0x00, 0x00, 0x00});

    ESP_LOGI(TAG, "Packet transmitted");
    return true;
}
