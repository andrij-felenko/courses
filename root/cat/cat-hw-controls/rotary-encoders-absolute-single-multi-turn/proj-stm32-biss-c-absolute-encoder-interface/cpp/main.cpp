#include <Arduino.h>
#include "AbsoluteEncoder.h"

// Прив'язка цифрових пінів для шини енкодера
constexpr uint8_t PIN_ENCODER_CLK = 6;
constexpr uint8_t PIN_ENCODER_DATA = 7;

// Конфігурація 25-бітного багатооборотного енкодера (12 біт оборотів + 13 біт кута)
const EncoderConfig encoderConfig = {
    .clkPin = PIN_ENCODER_CLK,
    .dataPin = PIN_ENCODER_DATA,
    .singleTurnBits = 13,
    .multiTurnBits = 12,
    .clockPeriodUs = 4,
    .useGrayCode = true
};

AbsoluteEncoder encoder(encoderConfig);

uint32_t lastReadTime = 0;
constexpr uint32_t READ_INTERVAL_MS = 100;

void setup() {
    Serial.begin(115200);
    while (!Serial && millis() < 3000) {
        // Очікування готовності послідовного порту
    }

    encoder.begin();
    Serial.println(F("Драйвер абсолютного енкодера ініціалізовано."));
}

void loop() {
    uint32_t now = millis();

    // Неблокувальне опитування за інтервалом
    if (now - lastReadTime >= READ_INTERVAL_MS) {
        lastReadTime = now;

        EncoderFrame frame = encoder.readFrame();

        if (frame.valid) {
            Serial.print(F("Оборот: "));
            Serial.print(frame.multiTurnCount);
            Serial.print(F(" | Кут: "));
            Serial.print(frame.singleTurnPosition);
            Serial.print(F(" / 8192 ("));
            float angleDeg = (frame.singleTurnPosition * 360.0f) / 8192.0f;
            Serial.print(angleDeg, 2);
            Serial.println(F(" deg)"));
        } else {
            Serial.print(F("Помилка кадру енкодера! CRC: "));
            Serial.print(frame.crcValid ? F("OK") : F("FAIL"));
            Serial.print(F(" | Error: "));
            Serial.print(frame.statusErr ? F("YES") : F("NO"));
            Serial.print(F(" | Warn: "));
            Serial.println(frame.statusWarn ? F("YES") : F("NO"));
        }
    }
}
