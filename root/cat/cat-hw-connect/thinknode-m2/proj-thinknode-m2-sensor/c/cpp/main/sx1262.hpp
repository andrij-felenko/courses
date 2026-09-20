#pragma once

#include <cstdint>
#include <span>
#include "driver/spi_master.h"

class SX1262 {
public:
    SX1262(int miso, int mosi, int clk, int cs, int busy);
    ~SX1262();

    bool init();
    bool transmit(std::span<const uint8_t> data);

private:
    void waitBusy() const;
    void writeCommand(uint8_t cmd, std::span<const uint8_t> args);

    int m_cs;
    int m_busy;
    spi_device_handle_t m_spi{nullptr};
};
