#include <Wire.h>
#include <Arduino.h>

class OV2640Diagnostic {
private:
    static const uint8_t OV2640_ADDR = 0x30;
    static const uint8_t BANK_SEL = 0xFF;
    static const uint8_t REG_PID = 0x0A;
    static const uint8_t REG_VER = 0x0B;

    uint8_t readRegister(uint8_t bank, uint8_t reg) {
        Wire.beginTransmission(OV2640_ADDR);
        Wire.write(BANK_SEL);
        Wire.write(bank);
        if (Wire.endTransmission() != 0) return 0x00;

        Wire.beginTransmission(OV2640_ADDR);
        Wire.write(reg);
        if (Wire.endTransmission() != 0) return 0x00;

        Wire.requestFrom(OV2640_ADDR, (uint8_t)1);
        if (Wire.available()) {
            return Wire.read();
        }
        return 0x00;
    }

public:
    bool verifyHardware() {
        uint8_t pid = readRegister(1, REG_PID);
        uint8_t ver = readRegister(1, REG_VER);

        if (pid == 0x26 && ver == 0x42) {
            Serial.println(F("[OK] Сенсор OV2640 відповідає на шині SCCB."));
            return true;
        } else {
            Serial.print(F("[ERR] Збій ідентифікації. Отримано PID: 0x"));
            Serial.print(pid, HEX);
            Serial.print(F(" VER: 0x"));
            Serial.println(ver, HEX);
            return false;
        }
    }
};
