#include <Arduino.h>

const int ADC_PIN = A0;
const float V_REF = 5.0;
const float SHUNT_OHM = 0.5;
const float AMP_GAIN = 10.0;
const int WINDOW_SIZE = 32;

const float I_DRY_THRESH = 0.040; // 40 мА
const float TEMP_LIMIT_C = 85.0;

enum PumpState {
    STATE_STARTUP,
    STATE_RUNNING,
    STATE_FAULT_DRY_RUN,
    STATE_COOLDOWN
};

class MicroPumpProtectionDriver {
private:
    PumpState state;
    float samples[WINDOW_SIZE];
    int sampleIdx;
    unsigned long stateStartTime;
    int faultCounter;

    float readCurrent() {
        int raw = analogRead(ADC_PIN);
        float v = (raw / 1023.0) * V_REF;
        return v / (AMP_GAIN * SHUNT_OHM);
    }

    float calculateRMS() {
        float sumSq = 0;
        for (int i = 0; i < WINDOW_SIZE; i++) {
            sumSq += samples[i] * samples[i];
        }
        return sqrt(sumSq / WINDOW_SIZE);
    }

public:
    MicroPumpProtectionDriver() : state(STATE_STARTUP), sampleIdx(0), faultCounter(0) {}

    void begin() {
        pinMode(ADC_PIN, INPUT);
        for (int i = 0; i < WINDOW_SIZE; i++) samples[i] = 0;
        stateStartTime = millis();
    }

    void update() {
        float iInstant = readCurrent();
        samples[sampleIdx] = iInstant;
        sampleIdx = (sampleIdx + 1) % WINDOW_SIZE;

        float iRMS = calculateRMS();
        unsigned long now = millis();

        switch (state) {
            case STATE_STARTUP:
                if (now - stateStartTime > 150) { // Пропуск пускового струму
                    state = STATE_RUNNING;
                }
                break;

            case STATE_RUNNING:
                if (iRMS < I_DRY_THRESH) {
                    faultCounter++;
                    if (faultCounter > 15) {
                        state = STATE_FAULT_DRY_RUN;
                        stateStartTime = now;
                        // Знеструмлення виходу
                        digitalWrite(LED_BUILTIN, HIGH);
                    }
                } else {
                    faultCounter = 0;
                }
                break;

            case STATE_FAULT_DRY_RUN:
                // Перехід у режим паузи
                state = STATE_COOLDOWN;
                break;

            case STATE_COOLDOWN:
                if (now - stateStartTime > 5000) { // Пауза 5 с
                    state = STATE_STARTUP;
                    stateStartTime = now;
                    digitalWrite(LED_BUILTIN, LOW);
                }
                break;
        }
    }

    PumpState getState() const { return state; }
    float getIrms() const { return calculateRMS(); }
};

MicroPumpProtectionDriver pumpDriver;

void setup() {
    Serial.begin(115200);
    pumpDriver.begin();
}

void loop() {
    pumpDriver.update();
    delay(10);
}
