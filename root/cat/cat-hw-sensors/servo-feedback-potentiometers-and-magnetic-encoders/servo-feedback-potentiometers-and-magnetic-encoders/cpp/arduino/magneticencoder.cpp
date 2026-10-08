// Зчитати 14-бітовий кут з магнітного енкодера через SPI
#include <SPI.h>

class MagneticEncoder {
private:
    uint8_t csPin;
public:
    MagneticEncoder(uint8_t pin) : csPin(pin) {}
    
    void begin() {
        pinMode(csPin, OUTPUT);
        digitalWrite(csPin, HIGH);
    }
    
    uint16_t readAngle() {
        SPI.beginTransaction(SPISettings(1000000, MSBFIRST, SPI_MODE1));
        digitalWrite(csPin, LOW);
        uint8_t highByte = SPI.transfer(0xFF);
        uint8_t lowByte = SPI.transfer(0xFF);
        digitalWrite(csPin, HIGH);
        SPI.endTransaction();
        
        uint16_t rawVal = ((uint16_t)highByte << 8) | lowByte;
        uint16_t parity = 0;
        for (uint16_t temp = rawVal; temp > 0; temp >>= 1) {
            parity ^= (temp & 1);
        }
        if (parity == 0) {
            return rawVal & 0x3FFF; // 14-бітна роздільна здатність
        }
        return 0xFFFF; // Помилка цілісності даних
    }
};
