#pragma once

#include <cstdint>
#include <cstddef>
#include <vector>
#include <span>

namespace CC1101 {

// Основні регістри та команди
constexpr uint8_t REG_SRES      = 0x30;
constexpr uint8_t REG_SFLUSHRX  = 0x3A;
constexpr uint8_t REG_SFLUSHTX  = 0x3B;
constexpr uint8_t REG_STX       = 0x35;
constexpr uint8_t REG_SRX       = 0x34;
constexpr uint8_t REG_SIDLE     = 0x36;
constexpr uint8_t REG_FIFO      = 0x3F;
constexpr uint8_t REG_MARCSTATE = 0xF5;
constexpr uint8_t REG_RXBYTES   = 0x3B | 0xC0;

// Структура пакету даних
struct Packet {
    std::vector<uint8_t> data;
};

// Інтерфейс для апаратного SPI
class ISpiBus {
public:
    virtual ~ISpiBus() = default;
    virtual void select() = 0;
    virtual void deselect() = 0;
    virtual uint8_t transfer(uint8_t data) = 0;
    virtual void delayMs(uint32_t ms) = 0;
};

// Об'єктно-орієнтований драйвер трансивера
class Transceiver {
public:
    explicit Transceiver(ISpiBus& spi);
    
    void init();
    void reset();
    
    void sendPacket(std::span<const uint8_t> payload);
    bool receivePacket(Packet& outPacket);
    
    void setIdle();
    void setRx();

private:
    void writeReg(uint8_t addr, uint8_t value);
    uint8_t readReg(uint8_t addr);
    void strobe(uint8_t cmd);

    ISpiBus& spi_;
};

} // namespace CC1101
