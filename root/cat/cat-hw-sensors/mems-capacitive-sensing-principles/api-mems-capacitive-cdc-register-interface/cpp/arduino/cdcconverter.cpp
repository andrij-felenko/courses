#include <Arduino.h>
#include <Wire.h>

class CDCConverter {
private:
    uint8_t _i2cAddr;
    uint8_t _drdyPin;
    float _fsrPf;
    static volatile bool _dataReady;

    static void IRAM_ATTR handleInterrupt() {
        _dataReady = true;
    }

public:
    CDCConverter(uint8_t addr, uint8_t drdyPin, float fsrPf = 4.0f)
        : _i2cAddr(addr), _drdyPin(drdyPin), _fsrPf(fsrPf) {}

    void begin() {
        pinMode(_drdyPin, INPUT_PULLUP);
        attachInterrupt(digitalPinToInterrupt(_drdyPin), handleInterrupt, FALLING);
    }

    bool readCapacitance(float &capacitancePf) {
        if (!_dataReady) return false;
        _dataReady = false;

        Wire.beginTransmission(_i2cAddr);
        Wire.write(0x02); // REG_DATA_MSB
        if (Wire.endTransmission(false) != 0) return false;

        if (Wire.requestFrom(_i2cAddr, (uint8_t)3) != 3) return false;

        uint32_t rawCode = ((uint32_t)Wire.read() << 16) |
                           ((uint32_t)Wire.read() << 8)  |
                            (uint32_t)Wire.read();

        float codeDiff = (float)rawCode - 8388608.0f;
        capacitancePf = (codeDiff / 16777215.0f) * _fsrPf;
        return true;
    }
};

volatile bool CDCConverter::_dataReady = false;
