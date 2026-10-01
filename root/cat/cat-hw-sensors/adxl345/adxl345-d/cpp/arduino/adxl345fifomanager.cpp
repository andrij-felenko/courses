#include <Arduino.h>
#include <Wire.h>

class ADXL345FIFOManager {
private:
    static constexpr uint8_t ADXL345_ADDR = 0x53;
    static constexpr uint8_t REG_INT_ENABLE = 0x2E;
    static constexpr uint8_t REG_INT_MAP = 0x2F;
    static constexpr uint8_t REG_FIFO_CTL = 0x38;

    void writeRegister(uint8_t reg, uint8_t val) {
        Wire.beginTransmission(ADXL345_ADDR);
        Wire.write(reg);
        Wire.write(val);
        Wire.endTransmission();
    }

public:
    void setupFIFOStream(uint8_t watermarkSamples) {
        // Режим Stream (біти 7:6 = 10) та поріг кількості відліків
        uint8_t fifoCtlVal = (2 << 6) | (watermarkSamples & 0x1F);
        
        writeRegister(REG_INT_MAP, 0x00);           // INT1 для всіх переривань
        writeRegister(REG_INT_ENABLE, (1 << 1));    // Дозвіл переривання Watermark
        writeRegister(REG_FIFO_CTL, fifoCtlVal);    // Активація Stream mode
    }
};
