#include <Arduino.h>
#include <Servo.h>

// Монітор захисту MG90S від аварійного заклинювання за струмовим шунтом
class MG90SStallGuard {
public:
    MG90SStallGuard(Servo& servoRef, uint8_t adcPin, float shuntResistanceOhms, 
                    float ampGain = 1.0f, float stallThresholdMa = 550.0f, 
                    unsigned long maxStallDurationMs = 150)
        : servo(servoRef), pin(adcPin), rShunt(shuntResistanceOhms),
          gain(ampGain), thresholdMa(stallThresholdMa), maxDurationMs(maxStallDurationMs) {}

    void begin() {
        stallStartTime = 0;
        isStalled = false;
        analogRead(pin); // Прогрів АЦП
    }

    // Періодична перевірка струму в циклі loop (інтервал 10 мс)
    void update() {
        if (!servo.attached() || isStalled) return;

        int rawAdc = analogRead(pin);
        float vAdc = (rawAdc * 5.0f) / 1023.0f; // Опорна напруга 5.0 В, 10-бітний АЦП

        // Розрахунок струму в міліамперах: I = (V_adc / Gain) / R_shunt * 1000
        float currentMa = ((vAdc / gain) / rShunt) * 1000.0f;
        unsigned long now = millis();

        if (currentMa >= thresholdMa) {
            if (stallStartTime == 0) {
                stallStartTime = now; // Фіксація початку перевантаження
            } else if (now - stallStartTime >= maxDurationMs) {
                // Струм блокування утримується довше допустимого часу
                triggerEmergencyDetach();
            }
        } else {
            stallStartTime = 0; // Скидання таймера, якщо це був штатний пусковий сплеск
        }
    }

    bool hasStalled() const { return isStalled; }

    void resetFault() {
        stallStartTime = 0;
        isStalled = false;
    }

private:
    void triggerEmergencyDetach() {
        servo.detach(); // Негайне зняття імпульсів ШІМ: знеструмлення H-моста
        isStalled = true;
        stallStartTime = 0;
        Serial.println(F("АВАРІЯ: Заклинювання MG90S! ШІМ знеструмлено для захисту обмоток."));
    }

    Servo& servo;
    uint8_t pin;
    float rShunt;
    float gain;
    float thresholdMa;
    unsigned long maxDurationMs;
    unsigned long stallStartTime = 0;
    bool isStalled = false;
};
