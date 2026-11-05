#include <Arduino.h>

const uint8_t STEP_PIN = 2;
const uint8_t DIR_PIN  = 3;

// --- Наївний підхід у циклі loop() ---
void naiveStepLoop(uint32_t steps, uint32_t stepIntervalUs) {
  digitalWrite(DIR_PIN, HIGH);
  for (uint32_t i = 0; i < steps; i++) {
    digitalWrite(STEP_PIN, HIGH);
    delayMicroseconds(2);
    digitalWrite(STEP_PIN, LOW);
    delayMicroseconds(stepIntervalUs - 2); // Блокує весь контролер
  }
}

// --- Детермінована концепція для періодичного ISR ---
struct StepGeneratorISR {
  uint32_t periodTicks;
  uint32_t tickCount;
  uint32_t currentStep;
  uint32_t totalSteps;
  bool pulseActive;

  void IRAM_ATTR handleTick() {
    if (pulseActive) {
      digitalWrite(STEP_PIN, LOW);
      pulseActive = false;
    }
    if (currentStep < totalSteps) {
      tickCount++;
      if (tickCount >= periodTicks) {
        tickCount = 0;
        digitalWrite(STEP_PIN, HIGH);
        pulseActive = true;
        currentStep++;
      }
    }
  }
};
