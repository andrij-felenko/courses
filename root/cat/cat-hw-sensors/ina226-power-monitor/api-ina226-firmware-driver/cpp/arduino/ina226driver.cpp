#include <Arduino.h>
#include <Wire.h>

class INA226Driver {
public:
    enum class Avg : uint16_t { Samples1 = 0x0000, Samples64 = 0x0600, Samples1024 = 0x0E00 };
    enum class ConvTime : uint16_t { Us1100 = 0x0004, Us2116 = 0x0005, Us8244 = 0x0007 };
    enum class Mode : uint16_t { PowerDown = 0x0000, Triggered = 0x0003, Continuous = 0x0007 };

    bool setConfiguration(Avg avg, ConvTime vbusCt, ConvTime vshCt, Mode mode) {
        uint16_t regVal = 0x4000 | static_cast<uint16_t>(avg) 
                          | (static_cast<uint16_t>(vbusCt) << 6) 
                          | (static_cast<uint16_t>(vshCt) << 3) 
                          | static_cast<uint16_t>(mode);
        return writeRegister(0x00, regVal);
    }
private:
    bool writeRegister(uint8_t reg, uint16_t val);
};
