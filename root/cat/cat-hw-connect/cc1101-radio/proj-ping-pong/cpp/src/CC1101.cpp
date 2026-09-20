#include "CC1101.hpp"

CC1101::CC1101(SpiHal& spi) : spi_(spi), state_(State::IDLE), rx_ready_(false), tx_busy_(false) {}

void CC1101::init() {
    spi_.init();
    reset();

    // Базові налаштування на 433 МГц (спрощено)
    writeReg(0x0B, 0x06); // FSCTRL1
    writeReg(0x0C, 0x00); // FSCTRL0
    writeReg(0x0D, 0x10); // FREQ2
    writeReg(0x0E, 0xA7); // FREQ1
    writeReg(0x0F, 0x62); // FREQ0
    writeReg(0x10, 0xC8); // MDMCFG4
    writeReg(0x11, 0x93); // MDMCFG3
    writeReg(0x12, 0x03); // MDMCFG2
    writeReg(0x18, 0x18); // MCSM0 (калібрування при переході в RX/TX)

    strobe(SRX);
    state_ = State::RX;
}

void CC1101::reset() {
    spi_.cs_low();
    while (!spi_.is_miso_low());
    spi_.transfer(SRES);
    while (!spi_.is_miso_low());
    spi_.cs_high();
}

void CC1101::writeReg(uint8_t addr, uint8_t value) {
    spi_.cs_low();
    spi_.transfer(addr);
    spi_.transfer(value);
    spi_.cs_high();
}

uint8_t CC1101::readReg(uint8_t addr) {
    spi_.cs_low();
    spi_.transfer(addr | READ_SINGLE);
    uint8_t val = spi_.transfer(0x00);
    spi_.cs_high();
    return val;
}

void CC1101::writeBurst(uint8_t addr, const uint8_t* data, uint8_t len) {
    spi_.cs_low();
    spi_.transfer(addr | WRITE_BURST);
    for (uint8_t i = 0; i < len; ++i) {
        spi_.transfer(data[i]);
    }
    spi_.cs_high();
}

void CC1101::readBurst(uint8_t addr, uint8_t* data, uint8_t len) {
    spi_.cs_low();
    spi_.transfer(addr | READ_BURST);
    for (uint8_t i = 0; i < len; ++i) {
        data[i] = spi_.transfer(0x00);
    }
    spi_.cs_high();
}

void CC1101::strobe(uint8_t cmd) {
    spi_.cs_low();
    spi_.transfer(cmd);
    spi_.cs_high();
}

void CC1101::update() {
    if (state_ == State::TX) {
        if (!spi_.get_gdo0()) { // Пін падає, коли передача завершена
            tx_busy_ = false;
            strobe(SRX);
            state_ = State::RX;
        }
    } else if (state_ == State::RX) {
        if (spi_.get_gdo0()) { // Пін піднімається, коли отримано синхро-слово, і падає після прийому
            uint8_t rxBytes = readReg(RXBYTES | READ_BURST) & 0x7F;
            if (rxBytes > 0) {
                uint8_t len;
                readBurst(0x3F, &len, 1); // Читаємо довжину з FIFO
                if (len > 0 && len <= 64) {
                    rx_buffer_.resize(len);
                    readBurst(0x3F, rx_buffer_.data(), len);
                    rx_ready_ = true;
                }
                strobe(SFRX);
                strobe(SRX);
            }
        }
    }
}

bool CC1101::send(const std::vector<uint8_t>& data) {
    if (state_ == State::TX || data.empty() || data.size() > 60) {
        return false;
    }
    
    strobe(SIDLE);
    strobe(SFTX); // Очищення TX FIFO
    
    uint8_t len = data.size();
    writeReg(0x3F, len); // Пишемо довжину у FIFO
    writeBurst(0x3F, data.data(), len);
    
    strobe(STX);
    state_ = State::TX;
    tx_busy_ = true;
    return true;
}

bool CC1101::receive(std::vector<uint8_t>& data) {
    if (rx_ready_) {
        data = rx_buffer_;
        rx_ready_ = false;
        return true;
    }
    return false;
}

CC1101::State CC1101::getState() const {
    return state_;
}
