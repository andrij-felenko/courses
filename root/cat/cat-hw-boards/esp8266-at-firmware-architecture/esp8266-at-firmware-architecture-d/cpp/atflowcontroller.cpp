#include <Arduino.h>

class AtFlowController {
private:
    HardwareSerial& _serial;
    const uint8_t _rtsPin;
    const uint8_t _ctsPin;

public:
    AtFlowController(HardwareSerial& serial, uint8_t rtsPin, uint8_t ctsPin)
        : _serial(serial), _rtsPin(rtsPin), _ctsPin(ctsPin) {}

    void begin(unsigned long baud) {
        pinMode(_rtsPin, INPUT);
        pinMode(_ctsPin, OUTPUT);
        digitalWrite(_ctsPin, LOW); // Готові до прийому даних (active LOW)
        
        // Ініціалізація послідовного порту
        _serial.begin(baud, SERIAL_8N1);
        Serial.println("AT Flow Controller ініціалізовано.");
    }

    bool sendPacedData(const uint8_t* payload, size_t length) {
        // Перевірка стану CTS сигналу від ESP8266 (якщо HIGH - лінія зайнята/буфери повні)
        if (digitalRead(_rtsPin) == HIGH) {
            Serial.println("Увага: ESP8266 підняв RTS! Буфери lwIP переповнені. Очікування...");
            unsigned long startWait = millis();
            while (digitalRead(_rtsPin) == HIGH) {
                if (millis() - startWait > 2000) {
                    Serial.println("Помилка: Таймаут очікування звільнення буферів!");
                    return false;
                }
                delay(10);
            }
        }

        // Формування AT-команди відправки
        _serial.printf("AT+CIPSEND=0,%u\r\n", (unsigned int)length);
        delay(15);

        // Передавання даних у послідовний порт
        size_t written = _serial.write(payload, length);
        return (written == length);
    }
};
