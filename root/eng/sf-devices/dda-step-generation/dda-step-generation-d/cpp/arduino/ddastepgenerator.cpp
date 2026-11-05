#include <Arduino.h>

const uint32_t ISR_FREQUENCY_HZ = 100000; // 100 кГц
const uint8_t  STEP_PIN_X        = 5;
const uint8_t  DIR_PIN_X         = 6;

class DdaStepGenerator {
private:
  uint32_t accumulator;
  uint32_t increment;
  uint32_t stepCounter;
  bool     pulseHigh;

public:
  DdaStepGenerator() : accumulator(0), increment(0), stepCounter(0), pulseHigh(false) {}

  void setFrequency(uint32_t stepFreqHz) {
    if (stepFreqHz >= ISR_FREQUENCY_HZ) {
      increment = 0xFFFFFFFF;
    } else {
      uint64_t val = ((uint64_t)stepFreqHz << 32) / ISR_FREQUENCY_HZ;
      increment = (uint32_t)val;
    }
  }

  void setDirection(bool clockwise) {
    digitalWrite(DIR_PIN_X, clockwise ? HIGH : LOW);
  }

  // Обробник одного такту ISR
  void IRAM_ATTR onIsrTick() {
    if (pulseHigh) {
      digitalWrite(STEP_PIN_X, LOW);
      pulseHigh = false;
    }

    if (increment == 0) return;

    uint32_t previousAccumulator = accumulator;
    accumulator += increment;

    // Автоматичне переповнення 32-бітного uint32_t при досягненні 2^32
    if (accumulator < previousAccumulator) {
      digitalWrite(STEP_PIN_X, HIGH);
      pulseHigh = true;
      stepCounter++;
    }
  }

  uint32_t getSteps() const { return stepCounter; }
};
