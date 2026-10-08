#include <Arduino.h>
#include <Wire.h>
#include "ina226_types.hpp"

class INA226Driver {
private:
    uint8_t  _address;
    TwoWire* _wire;

    static constexpr uint8_t REG_CONFIG      = 0x00;
    static constexpr uint8_t REG_MASK_ENABLE = 0x06;
    static constexpr uint16_t BIT_CVRF       = (1 << 3);
    static constexpr uint16_t BIT_RST        = (1 << 15);

    bool writeRegister(uint8_t reg, uint16_t val) {
        _wire->beginTransmission(_address);
        _wire->write(reg);
        _wire->write(static_cast<uint8_t>(val >> 8));   // MSB
        _wire->write(static_cast<uint8_t>(val & 0xFF)); // LSB
        return (_wire->endTransmission() == 0);
    }

    bool readRegister(uint8_t reg, uint16_t& val) {
        _wire->beginTransmission(_address);
        _wire->write(reg);
        if (_wire->endTransmission() != 0) return false;

        if (_wire->requestFrom(_address, static_cast<uint8_t>(2)) == 2) {
            uint8_t msb = _wire->read();
            uint8_t lsb = _wire->read();
            val = (static_cast<uint16_t>(msb) << 8) | lsb;
            return true;
        }
        return false;
    }

public:
    INA226Driver(uint8_t addr = 0x40, TwoWire* wire = &Wire)
        : _address(addr), _wire(wire) {}

    bool begin(const INA226::Config& config) {
        // Програмне скидання
        if (!writeRegister(REG_CONFIG, BIT_RST)) return false;
        delay(1);

        // Запис конфігурації
        return writeRegister(REG_CONFIG, config.toRegisterValue());
    }

    bool isDataReady() {
        uint16_t maskReg = 0;
        if (readRegister(REG_MASK_ENABLE, maskReg)) {
            return (maskReg & BIT_CVRF) != 0;
        }
        return false;
    }
};
