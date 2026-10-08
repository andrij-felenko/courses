#include <Arduino.h>

const uint8_t PIN_TCRT_AO = A0;  // Аналоговий вхід (колектор TCRT5000)
const uint8_t PIN_IR_LED  = 3;   // Вихід керування анодом ІЧ-світлодіода

struct SensorCalibration {
    uint16_t white_val = 1023;  // Мінімальний аналоговий відгук (біле)
    uint16_t black_val = 0;     // Максимальний аналоговий відгук (чорне)
    uint16_t threshold = 512;   // Розрахований адаптивний поріг
    bool saturated = false;     // Прапор засвічення
};

SensorCalibration tcrt_calib;

// Перевірка наявності фонового засвічення (LED OFF)
bool checkAmbientSaturation() {
    digitalWrite(PIN_IR_LED, LOW);
    delayMicroseconds(200);
    uint16_t ambient_val = analogRead(PIN_TCRT_AO);
    
    // Якщо при вимкненому LED значення A0 падає нижче 200 (при 10-біт АЦП 0..1023),
    // фототранзистор увійшов у режим насичення від зовнішнього світла
    return (ambient_val < 200);
}

// Програмоване калібрування порогового рівня під час руху над поверхнею
void performAutoCalibration(uint16_t duration_ms) {
    digitalWrite(PIN_IR_LED, HIGH);
    delay(5);

    uint32_t start_time = millis();
    tcrt_calib.white_val = 1023;
    tcrt_calib.black_val = 0;

    while (millis() - start_time < duration_ms) {
        uint16_t current_val = analogRead(PIN_TCRT_AO);
        if (current_val < tcrt_calib.white_val) tcrt_calib.white_val = current_val;
        if (current_val > tcrt_calib.black_val) tcrt_calib.black_val = current_val;
        delay(5);
    }

    // Розрахунок адаптивного порогового значення
    tcrt_calib.threshold = tcrt_calib.white_val + (tcrt_calib.black_val - tcrt_calib.white_val) / 2;
}

void setup() {
    Serial.begin(115200);
    pinMode(PIN_IR_LED, OUTPUT);
    
    // Перевірка фонового засвічення перед стартом
    if (checkAmbientSaturation()) {
        Serial.println("УВАГА: Виявлено критичне оптичне засвічення!");
        tcrt_calib.saturated = true;
    } else {
        Serial.println("Фонове освітлення в нормі. Запуск калібрування...");
        performAutoCalibration(3000); // 3 секунди на калібрування над лінією
    }
}

void loop() {
    digitalWrite(PIN_IR_LED, HIGH);
    delayMicroseconds(100);
    uint16_t val = analogRead(PIN_TCRT_AO);
    
    bool is_on_line = (val > tcrt_calib.threshold);
    
    Serial.print("АЦП: ");
    Serial.print(val);
    Serial.print(" | Поріг: ");
    Serial.print(tcrt_calib.threshold);
    Serial.print(" | Стан: ");
    Serial.println(is_on_line ? "ЧОРНА ЛІНІЯ" : "БІЛЕ ПОЛЕ");
    
    delay(50);
}
