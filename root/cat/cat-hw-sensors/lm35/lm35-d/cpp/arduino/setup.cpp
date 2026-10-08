#include <Arduino.h>

const int LM35_PIN = A0;
const float FILTER_ALPHA = 0.1f;
float filtered_adc = 0.0f;

void setup() {
    Serial.begin(115200);
#if defined(__AVR_ATmega328P__)
    analogReference(INTERNAL); // Внутрішнє джерело 1.1 В для ATmega328P
#endif
}

float readTemperatureC() {
    int raw_adc = analogRead(LM35_PIN);
    if (filtered_adc == 0.0f) {
        filtered_adc = raw_adc;
    } else {
        filtered_adc = FILTER_ALPHA * (float)raw_adc + (1.0f - FILTER_ALPHA) * filtered_adc;
    }
    
    // Розрахунок для 10-бітного АЦП з опорною напругою 1100 мВ
    float voltage_mv = (filtered_adc / 1024.0f) * 1100.0f;
    float temp_c = voltage_mv / 10.0f; // 10 мВ/°C
    return temp_c;
}

void loop() {
    float temp = readTemperatureC();
    Serial.print("Температура: ");
    Serial.print(temp, 2);
    Serial.println(" °C");
    delay(100);
}
