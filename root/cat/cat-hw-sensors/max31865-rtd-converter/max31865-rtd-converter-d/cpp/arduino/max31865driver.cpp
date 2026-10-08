#include <Arduino.h>
#include <SPI.h>

class MAX31865Driver {
public:
    MAX31865Driver(uint8_t csPin, float rRef = 400.0f, float r0 = 100.0f)
        : _csPin(csPin), _rRef(rRef), _r0(r0) {}

    void begin(bool is3Wire = false) {
        pinMode(_csPin, OUTPUT);
        digitalWrite(_csPin, HIGH);

        uint8_t config = 0x80 | 0x40 | 0x01; // Vbias ON, Auto mode, 50Hz filter
        if (is3Wire) {
            config |= 0x10; // 3-wire mode
        }
        config |= 0x02; // Clear fault flags

        writeRegister(0x00, config);
    }

    bool readTemperature(float &temperature) {
        uint8_t msb = readRegister(0x01);
        uint8_t lsb = readRegister(0x02);

        uint16_t rawVal = ((uint16_t)msb << 8) | lsb;
        if (rawVal & 0x01) {
            return false; // Fault flag set
        }

        uint16_t adcCode = rawVal >> 1;
        float rRtd = ((float)adcCode * _rRef) / 32768.0f;

        const float A = 3.9083e-3f;
        const float B = -5.775e-7f;

        float rRatio = rRtd / _r0;
        float discriminant = (A * A) - (4.0f * B * (1.0f - rRatio));

        if (discriminant < 0.0f) {
            return false;
        }

        float temp = (-A + sqrtf(discriminant)) / (2.0f * B);

        if (temp < 0.0f) {
            float rNorm = (rRtd / _r0) * 100.0f;
            temp = -242.02f + (2.2228f * rNorm) + (2.5859e-3f * rNorm * rNorm)
                   - (4.8260e-6f * rNorm * rNorm * rNorm);
        }

        temperature = temp;
        return true;
    }

private:
    uint8_t _csPin;
    float _rRef;
    float _r0;

    void writeRegister(uint8_t reg, uint8_t val) {
        digitalWrite(_csPin, LOW);
        SPI.transfer(reg | 0x80);
        SPI.transfer(val);
        digitalWrite(_csPin, HIGH);
    }

    uint8_t readRegister(uint8_t reg) {
        digitalWrite(_csPin, LOW);
        SPI.transfer(reg & 0x7F);
        uint8_t val = SPI.transfer(0x00);
        digitalWrite(_csPin, HIGH);
        return val;
    }
};
