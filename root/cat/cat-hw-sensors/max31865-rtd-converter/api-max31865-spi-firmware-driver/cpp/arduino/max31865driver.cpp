#include <Arduino.h>
#include <SPI.h>

class MAX31865Driver {
private:
    uint8_t _cs_pin;
    SPISettings _spi_settings;

    void writeRegister(uint8_t reg, uint8_t value) {
        SPI.beginTransaction(_spi_settings);
        digitalWrite(_cs_pin, LOW);
        SPI.transfer(reg | 0x80); // A7 = 1 для запису
        SPI.transfer(value);
        digitalWrite(_cs_pin, HIGH);
        SPI.endTransaction();
    }

    uint8_t readRegister(uint8_t reg) {
        SPI.beginTransaction(_spi_settings);
        digitalWrite(_cs_pin, LOW);
        SPI.transfer(reg & 0x7F); // A7 = 0 для читання
        uint8_t val = SPI.transfer(0x00);
        digitalWrite(_cs_pin, HIGH);
        SPI.endTransaction();
        return val;
    }

public:
    MAX31865Driver(uint8_t cs_pin) 
        : _cs_pin(cs_pin), _spi_settings(5000000, MSBFIRST, SPI_MODE1) {}

    void begin() {
        pinMode(_cs_pin, OUTPUT);
        digitalWrite(_cs_pin, HIGH);
        SPI.begin();
    }

    uint16_t readRTDRaw(bool &fault_detected) {
        // Увімкнення VBIAS та старту 1-Shot
        writeRegister(0x00, 0x80 | 0x20);
        delay(25); // Затримка конверсії 60 Гц

        // Burst-читання 2 байтів з 0x01
        SPI.beginTransaction(_spi_settings);
        digitalWrite(_cs_pin, LOW);
        SPI.transfer(0x01 & 0x7F);
        uint8_t msb = SPI.transfer(0x00);
        uint8_t lsb = SPI.transfer(0x00);
        digitalWrite(_cs_pin, HIGH);
        SPI.endTransaction();

        uint16_t raw16 = ((uint16_t)msb << 8) | lsb;
        fault_detected = (raw16 & 0x01) != 0;
        return (raw16 >> 1);
    }

    void handleFaults() {
        uint8_t status = readRegister(0x07);
        if (status != 0) {
            Serial.print(F("Помилка MAX31865! Код 0x07: 0x"));
            Serial.println(status, HEX);
            // Скидання статусу помилки
            writeRegister(0x00, 0x02);
        }
    }
};
