#include <Arduino.h>

struct INA226Measurement {
    float busVoltageV;
    float currentA;
    float powerW;
};

class INA226Reader {
public:
    bool isConversionReady() {
        uint16_t maskReg = readRegister(0x06);
        return (maskReg & 0x0008) != 0; // біт CVRF
    }

    bool readMeasurement(float currentLsb, INA226Measurement &out) {
        int16_t rawBus = static_cast<int16_t>(readRegister(0x02));
        int16_t rawCurrent = static_cast<int16_t>(readRegister(0x04));
        uint16_t rawPower = readRegister(0x03);

        out.busVoltageV = rawBus * 0.00125f;
        out.currentA = rawCurrent * currentLsb;
        out.powerW = rawPower * (25.0f * currentLsb);
        return true;
    }
private:
    uint16_t readRegister(uint8_t reg);
};
