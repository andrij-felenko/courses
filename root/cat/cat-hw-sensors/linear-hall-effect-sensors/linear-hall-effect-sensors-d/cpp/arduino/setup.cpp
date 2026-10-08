#include <Arduino.h>

const int HALL_PIN = A0;
const float EMA_ALPHA = 0.15f; // Smoothing factor
const float ADC_RESOLUTION = 1023.0f; // 10-bit ADC for standard ATmega328P
const float VCC_VOLTAGE = 5.0f; // Ratiometric reference voltage

float filtered_adc_code = 512.0f; // Midpoint for 10-bit ADC

void setup() {
    Serial.begin(115200);
    pinMode(HALL_PIN, INPUT);
}

float readFilteredHall() {
    int raw_val = analogRead(HALL_PIN);
    // Exponential Moving Average filter
    filtered_adc_code = (EMA_ALPHA * (float)raw_val) + ((1.0f - EMA_ALPHA) * filtered_adc_code);
    return filtered_adc_code;
}

void loop() {
    float adc_val = readFilteredHall();
    // Calculate measured voltage
    float voltage = (adc_val / ADC_RESOLUTION) * VCC_VOLTAGE;
    
    Serial.print("ADC Raw/Filtered: ");
    Serial.print(adc_val, 1);
    Serial.print(" | Sensor Output Voltage: ");
    Serial.print(voltage, 3);
    Serial.println(" V");
    
    delay(10);
}
