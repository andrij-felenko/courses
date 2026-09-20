#include <Arduino.h>
#include "ThumbwheelBcd.h"

// Прив'язка шини даних BCD (4 загальні лінії даних)
constexpr uint8_t PIN_BCD_1 = 2;
constexpr uint8_t PIN_BCD_2 = 3;
constexpr uint8_t PIN_BCD_4 = 4;
constexpr uint8_t PIN_BCD_8 = 5;

// Піни селекторів 3-х декад барабанного перемикача (Одиниці, Десятки, Сотні)
const uint8_t DIGIT_PINS[] = {6, 7, 8};

// Налаштування конфігурації
const BcdPinConfig config = {
    .pinBit1 = PIN_BCD_1,
    .pinBit2 = PIN_BCD_2,
    .pinBit4 = PIN_BCD_4,
    .pinBit8 = PIN_BCD_8,
    .digitEnablePins = DIGIT_PINS,
    .digitCount = 3,
    .debounceMs = 50
};

// Екземпляр класу драйвера
ThumbwheelBcd thumbwheel(config);

void setup() {
    Serial.begin(115200);
    while (!Serial && millis() < 3000) {
        // Очікування ініціалізації послідовного порту
    }

    thumbwheel.begin();
    Serial.println(F("Драйвер BCD-перемикача ініціалізовано."));
}

void loop() {
    // Неблокувальне оновлення стану у кожному циклі
    thumbwheel.update();

    // Фіксація зміни уставки
    if (thumbwheel.hasChanged()) {
        Serial.print(F("Нова встановлена уставка: "));
        Serial.println(thumbwheel.getValue());
    }

    // Фонова робота системи без затримок delay()
}
