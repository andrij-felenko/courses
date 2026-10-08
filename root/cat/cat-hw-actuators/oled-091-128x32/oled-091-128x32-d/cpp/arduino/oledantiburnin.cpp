#include <Wire.h>

#define OLED_I2C_ADDR 0x3C

class OLEDAntiBurnin {
private:
    uint32_t lastShiftTime;
    uint32_t lastActivityTime;
    uint8_t shiftStep;
    bool isSleeping;

    void sendCommand(uint8_t cmd) {
        Wire.beginTransmission(OLED_I2C_ADDR);
        Wire.write(0x00);
        Wire.write(cmd);
        Wire.endTransmission();
    }

public:
    OLEDAntiBurnin() : lastShiftTime(0), lastActivityTime(0), shiftStep(0), isSleeping(false) {}

    void registerUserActivity() {
        lastActivityTime = millis();
        if (isSleeping) {
            wakeUp();
        }
    }

    void setContrast(uint8_t contrast) {
        Wire.beginTransmission(OLED_I2C_ADDR);
        Wire.write(0x00);
        Wire.write(0x81);
        Wire.write(contrast);
        Wire.endTransmission();
    }

    void sleep() {
        sendCommand(0xAE); // Display OFF
        Wire.beginTransmission(OLED_I2C_ADDR);
        Wire.write(0x00);
        Wire.write(0x8D);
        Wire.write(0x10); // Disable charge pump
        Wire.endTransmission();
        isSleeping = true;
    }

    void wakeUp() {
        Wire.beginTransmission(OLED_I2C_ADDR);
        Wire.write(0x00);
        Wire.write(0x8D);
        Wire.write(0x14); // Enable charge pump
        Wire.endTransmission();
        sendCommand(0xAF); // Display ON
        isSleeping = false;
    }

    void tick() {
        uint32_t now = millis();
        
        // Автоматичний перехід у сон після 60 секунд бездіяльності
        if (!isSleeping && (now - lastActivityTime > 60000)) {
            sleep();
        }
    }
};
