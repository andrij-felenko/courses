#include <Arduino.h>

const int SENSOR_PIN = A0;
const unsigned long SAMPLE_INTERVAL_MS = 40;

unsigned long lastSampleTime = 0;
int smoothedValue = 0;

void setup() {
    Serial.begin(115200);
    pinMode(SENSOR_PIN, INPUT);
}

void loop() {
    unsigned long currentTime = millis();
    
    if (currentTime - lastSampleTime >= SAMPLE_INTERVAL_MS) {
        lastSampleTime = currentTime;
        
        int rawValue = analogRead(SENSOR_PIN);
        
        if (smoothedValue == 0) {
            smoothedValue = rawValue;
        } else {
            // Згладжування цифровим фільтром
            smoothedValue = (smoothedValue * 3 + rawValue) / 4;
        }
    }
}
