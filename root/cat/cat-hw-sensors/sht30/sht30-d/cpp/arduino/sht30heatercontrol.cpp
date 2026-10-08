#include <Arduino.h>
#include <Wire.h>

class SHT30HeaterControl {
private:
    static const uint8_t SHT30_I2C_ADDR = 0x44;
    static const uint16_t CMD_HEATER_ENABLE = 0x306D;
    static const uint16_t CMD_HEATER_DISABLE = 0x3066;
    static const uint16_t CMD_READ_STATUS = 0xF32D;

public:
    // Надсилання 16-бітної команди по шині I2C
    static bool sendCommand(uint16_t cmd) {
        Wire.beginTransmission(SHT30_I2C_ADDR);
        Wire.write(static_cast<uint8_t>(cmd >> 8));
        Wire.write(static_cast<uint8_t>(cmd & 0xFF));
        return (Wire.endTransmission() == 0);
    }

    // Опитування регістра стану для перевірки працездатності нагрівача (біт 13)
    static bool isHeaterActive() {
        Wire.beginTransmission(SHT30_I2C_ADDR);
        Wire.write(static_cast<uint8_t>(CMD_READ_STATUS >> 8));
        Wire.write(static_cast<uint8_t>(CMD_READ_STATUS & 0xFF));
        if (Wire.endTransmission(false) != 0) return false;

        if (Wire.requestFrom(SHT30_I2C_ADDR, static_cast<uint8_t>(3)) == 3) {
            uint8_t msb = Wire.read();
            uint8_t lsb = Wire.read();
            Wire.read(); // Пропускаємо байт CRC-8
            uint16_t status = (static_cast<uint16_t>(msb) << 8) | lsb;
            return (status & (1 << 13)) != 0;
        }
        return false;
    }

    // Процедура сушіння полімерного діелектрика
    static void executeDewRecovery() {
        Serial.println(F("Активація мікронагрівача SHT30..."));
        if (sendCommand(CMD_HEATER_ENABLE)) {
            delay(2000); // 2 секунди інтенсивного випаровування роси

            if (isHeaterActive()) {
                Serial.println(F("Нагрівач працює: випаровування рідкої вологи."));
            }

            Serial.println(F("Деактивація нагрівача..."));
            sendCommand(CMD_HEATER_DISABLE);

            Serial.println(F("Очікування термічної стабілізації (5 секунд)..."));
            delay(5000); // Охолодження підкладки до температури середовища
            Serial.println(F("Давач готов до відновлення вимірювань."));
        }
    }
};
