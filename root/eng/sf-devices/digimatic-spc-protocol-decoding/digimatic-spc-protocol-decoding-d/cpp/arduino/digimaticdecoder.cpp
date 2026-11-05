#include <Arduino.h>

class DigimaticDecoder {
private:
    uint8_t _reqPin;
    uint8_t _clkPin;
    uint8_t _dataPin;

public:
    DigimaticDecoder(uint8_t req, uint8_t clk, uint8_t data)
        : _reqPin(req), _clkPin(clk), _dataPin(data) {}

    void begin() {
        pinMode(_reqPin, OUTPUT);
        digitalWrite(_reqPin, HIGH);
        pinMode(_clkPin, INPUT_PULLUP);
        pinMode(_dataPin, INPUT_PULLUP);
    }

    bool readMeasurement(double &outputValue, bool &isInch) {
        uint8_t nibbles[13] = {0};

        // Генерація імпульсу запиту REQ
        digitalWrite(_reqPin, LOW);
        delayMicroseconds(500);
        digitalWrite(_reqPin, HIGH);

        // Зчитування 13 півбайтів (52 біти)
        for (int i = 0; i < 13; i++) {
            uint8_t nibble = 0;
            for (int b = 0; b < 4; b++) {
                // Очікування спадаючого фронту CLK з таймаутом 5 мс
                uint32_t startUs = micros();
                while (digitalRead(_clkPin) == HIGH) {
                    if (micros() - startUs > 5000) return false;
                }
                
                uint8_t bitVal = digitalRead(_dataPin) == HIGH ? 1 : 0;
                nibble |= (bitVal << b);

                while (digitalRead(_clkPin) == LOW) {
                    if (micros() - startUs > 5000) return false;
                }
            }
            nibbles[i] = nibble;
        }

        // Перевірка преамбули
        if (nibbles[0] != 0x0F || nibbles[1] != 0x0F) return false;

        long raw = nibbles[5] + nibbles[6]*10 + nibbles[7]*100 + 
                   nibbles[8]*1000 + nibbles[9]*10000 + nibbles[10]*100000;

        double divisor = 1.0;
        for (int exp = 0; exp < nibbles[11]; exp++) {
            divisor *= 10.0;
        }

        outputValue = (double)raw / divisor;
        if (nibbles[4] & 0x08) {
            outputValue = -outputValue;
        }
        isInch = (nibbles[12] & 0x01) != 0;

        return true;
    }
};
