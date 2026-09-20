#pragma once

#include "spi_hal.hpp"
#include <cstdint>
#include <vector>

class CC1101 {
public:
    enum class State {
        IDLE,
        RX,
        TX
    };

    CC1101(SpiHal& spi);

    void init();
    void update();
    bool send(const std::vector<uint8_t>& data);
    bool receive(std::vector<uint8_t>& data);
    State getState() const;

private:
    SpiHal& spi_;
    State state_;
    std::vector<uint8_t> rx_buffer_;
    bool rx_ready_;
    bool tx_busy_;

    void reset();
    void writeReg(uint8_t addr, uint8_t value);
    uint8_t readReg(uint8_t addr);
    void writeBurst(uint8_t addr, const uint8_t* data, uint8_t len);
    void readBurst(uint8_t addr, uint8_t* data, uint8_t len);
    void strobe(uint8_t cmd);

    static constexpr uint8_t WRITE_BURST = 0x40;
    static constexpr uint8_t READ_SINGLE = 0x80;
    static constexpr uint8_t READ_BURST  = 0xC0;

    static constexpr uint8_t SRES  = 0x30;
    static constexpr uint8_t SRX   = 0x34;
    static constexpr uint8_t STX   = 0x35;
    static constexpr uint8_t SIDLE = 0x36;
    static constexpr uint8_t SFRX  = 0x3A;
    static constexpr uint8_t SFTX  = 0x3B;

    static constexpr uint8_t RXBYTES = 0x3B;
};
