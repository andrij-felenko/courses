// Приклад ініціалізації OV3640 та перемикання банок у C++ (Arduino Framework)
#include <Arduino.h>
#include <Wire.h>

class OV3640Camera {
private:
    static const uint8_t SCCB_ADDR = 0x3C;
    static const uint8_t REG_BANK_SEL = 0xFF;

public:
    bool writeRegister(uint8_t reg, uint8_t val) {
        Wire.beginTransmission(SCCB_ADDR);
        Wire.write(reg);
        Wire.write(val);
        return (Wire.endTransmission() == 0);
    }

    uint8_t readRegister(uint8_t reg) {
        Wire.beginTransmission(SCCB_ADDR);
        Wire.write(reg);
        Wire.endTransmission(false); // Repeated start
        Wire.requestFrom(SCCB_ADDR, (uint8_t)1);
        return Wire.available() ? Wire.read() : 0x00;
    }

    bool checkDeviceID() {
        // Вибір Bank 1 для доступу до системного ID
        writeRegister(REG_BANK_SEL, 0x01);
        
        uint8_t idHigh = readRegister(0x0A);
        uint8_t idLow  = readRegister(0x0B);
        uint16_t chipId = ((uint16_t)idHigh << 8) | idLow;

        if (chipId == 0x3640) {
            Serial.println(F("OV3640 виявлено успішно!"));
            return true;
        } else {
            Serial.print(F("Збій виявлення OV3640, прочитано ID: 0x"));
            Serial.println(chipId, HEX);
            return false;
        }
    }
};
