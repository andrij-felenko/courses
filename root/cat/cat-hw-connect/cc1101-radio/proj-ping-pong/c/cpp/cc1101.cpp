#include "cc1101.hpp"

namespace CC1101 {

Transceiver::Transceiver(ISpiBus& spi) : spi_(spi) {}

void Transceiver::writeReg(uint8_t addr, uint8_t value) {
    spi_.select();
    spi_.transfer(addr);
    spi_.transfer(value);
    spi_.deselect();
}

uint8_t Transceiver::readReg(uint8_t addr) {
    spi_.select();
    spi_.transfer(addr | 0x80);
    uint8_t val = spi_.transfer(0x00);
    spi_.deselect();
    return val;
}

void Transceiver::strobe(uint8_t cmd) {
    spi_.select();
    spi_.transfer(cmd);
    spi_.deselect();
}

void Transceiver::reset() {
    spi_.select();
    spi_.delayMs(1);
    spi_.deselect();
    spi_.delayMs(1);
    strobe(REG_SRES);
}

void Transceiver::init() {
    reset();
    
    // Мінімально необхідне налаштування для прикладу
    writeReg(0x0B, 0x06); // FSCTRL1
    writeReg(0x0C, 0x00); // FSCTRL0
}

void Transceiver::setIdle() {
    strobe(REG_SIDLE);
    while (readReg(REG_MARCSTATE) != 0x01) {
        // Очікування режиму IDLE
    }
}

void Transceiver::setRx() {
    setIdle();
    strobe(REG_SRX);
}

void Transceiver::sendPacket(std::span<const uint8_t> payload) {
    setIdle();
    strobe(REG_SFLUSHTX);
    
    spi_.select();
    spi_.transfer(REG_FIFO);
    spi_.transfer(static_cast<uint8_t>(payload.size()));
    for (uint8_t byte : payload) {
        spi_.transfer(byte);
    }
    spi_.deselect();
    
    strobe(REG_STX);
}

bool Transceiver::receivePacket(Packet& outPacket) {
    uint8_t rxBytes = readReg(REG_RXBYTES);
    if (rxBytes > 0) {
        uint8_t length = readReg(REG_FIFO);
        if (length > 0 && length <= 64) {
            outPacket.data.resize(length);
            
            spi_.select();
            spi_.transfer(REG_FIFO | 0x80); // Бурстове читання
            for (uint8_t i = 0; i < length; i++) {
                outPacket.data[i] = spi_.transfer(0x00);
            }
            spi_.deselect();
            
            setIdle();
            strobe(REG_SFLUSHRX);
            return true;
        } else {
            // Некоректний розмір
            setIdle();
            strobe(REG_SFLUSHRX);
            return false;
        }
    }
    return false;
}

} // namespace CC1101
