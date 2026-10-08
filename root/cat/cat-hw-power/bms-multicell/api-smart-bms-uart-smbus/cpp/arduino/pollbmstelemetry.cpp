// Приклад неблокуючого драйвера зчитування BMS для Arduino (C++)
#include <Arduino.h>

enum BmsState { BMS_IDLE, BMS_WAIT_RESPONSE, BMS_PROCESS_DATA, BMS_ERROR };
BmsState currentState = BMS_IDLE;

unsigned long requestTimestamp = 0;
const unsigned long RESPONSE_TIMEOUT_MS = 150;
uint8_t rxBuffer[32];
uint8_t rxIndex = 0;

void pollBmsTelemetry() {
    switch (currentState) {
        case BMS_IDLE:
            // Формування та відправка кадру запиту 0x03
            Serial1.write(0xDD);
            Serial1.write(0xA5);
            Serial1.write(0x03);
            Serial1.write(0x00);
            Serial1.write(0xFF);
            Serial1.write(0xFD);
            Serial1.write(0x77);
            
            rxIndex = 0;
            requestTimestamp = millis();
            currentState = BMS_WAIT_RESPONSE;
            break;

        case BMS_WAIT_RESPONSE:
            while (Serial1.available()) {
                rxBuffer[rxIndex++] = Serial1.read();
                if (rxIndex >= 10) { // Отримано повний кадр
                    currentState = BMS_PROCESS_DATA;
                    break;
                }
            }
            if (millis() - requestTimestamp > RESPONSE_TIMEOUT_MS) {
                currentState = BMS_ERROR;
            }
            break;

        case BMS_PROCESS_DATA:
            // Розбір даних та перевірка CRC
            currentState = BMS_IDLE;
            break;

        case BMS_ERROR:
            // Обробка таймауту або CRC, повторна спроба
            currentState = BMS_IDLE;
            break;
    }
}
