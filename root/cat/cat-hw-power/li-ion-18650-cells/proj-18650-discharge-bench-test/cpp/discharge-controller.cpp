// Класова реалізація автоматизованого контролера стенда розряду з керуванням керованим навантаженням та захисними інтервалами моніторингу
#include <Arduino.h>

class DischargeController {
private:
    uint8_t loadPin;
    float cutoffVoltage;
    float maxTemp;
    bool isDischarging;

public:
    DischargeController(uint8_t pin, float cutV, float maxT) 
        : loadPin(pin), cutoffVoltage(cutV), maxTemp(maxT), isDischarging(false) {
        pinMode(loadPin, OUTPUT);
        digitalWrite(loadPin, LOW);
    }

    void start() {
        isDischarging = true;
        digitalWrite(loadPin, HIGH);
    }

    void stop() {
        isDischarging = false;
        digitalWrite(loadPin, LOW);
    }

    void update(float currentVoltage, float currentTemp) {
        if (!isDischarging) return;

        if (currentVoltage <= cutoffVoltage || currentTemp >= maxTemp) {
            stop();
            Serial.println("Cutoff reached. Discharge stopped.");
        }
    }
};
