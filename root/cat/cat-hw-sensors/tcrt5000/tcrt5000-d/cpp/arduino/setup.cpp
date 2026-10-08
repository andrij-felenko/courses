#include <Arduino.h>

const uint8_t PIN_TCRT_AO = A0;  // Аналоговий вихід TCRT5000 (колектор)
const uint8_t PIN_TCRT_DO = 2;   // Цифровий вихід компаратора LM393
const uint8_t PIN_IR_LED  = 3;   // Пін керування анодом ІЧ-світлодіода

int threshold_value = 500;       // Програмний поріг розпізнавання чорне/біле

void setup() {
    Serial.begin(115200);
    pinMode(PIN_TCRT_DO, INPUT);
    pinMode(PIN_IR_LED, OUTPUT);
    digitalWrite(PIN_IR_LED, LOW);
}

// Функція зчитування аналогового рівня з відніманням фону
uint16_t readTCRTModulated() {
    // 1. Зчитуємо рівень фонового засвічення (LED OFF)
    digitalWrite(PIN_IR_LED, LOW);
    delayMicroseconds(100);
    uint16_t bg_light = analogRead(PIN_TCRT_AO);

    // 2. Зчитуємо рівень з активним зондувальним променем (LED ON)
    digitalWrite(PIN_IR_LED, HIGH);
    delayMicroseconds(100);
    uint16_t active_light = analogRead(PIN_TCRT_AO);

    digitalWrite(PIN_IR_LED, LOW);

    // Фототранзистор відкривається під світлом, знижуючи напругу
    if (bg_light > active_light) {
        return (bg_light - active_light);
    }
    return 0;
}

void loop() {
    uint16_t analog_signal = readTCRTModulated();
    bool is_white = (analog_signal > threshold_value);

    Serial.print("Сигнал відбивання: ");
    Serial.print(analog_signal);
    Serial.print(" | Стан: ");
    Serial.println(is_white ? "БІЛИЙ" : "ЧОРНИЙ");

    delay(100);
}
