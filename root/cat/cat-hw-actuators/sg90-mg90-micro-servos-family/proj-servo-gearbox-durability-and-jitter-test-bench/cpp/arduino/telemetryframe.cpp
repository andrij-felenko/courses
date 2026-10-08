#include <Arduino.h>

// Структура кадру телеметрії для збереження стану стенда
struct TelemetryFrame {
    uint32_t timestampMs;
    float targetAngleDeg;
    float actualAngleDeg;
};

const uint16_t RING_BUFFER_SIZE = 128;
TelemetryFrame ringBuffer[RING_BUFFER_SIZE];
volatile uint16_t headIdx = 0;
volatile uint16_t tailIdx = 0;

void logTelemetryPoint(float targetAngle, float currentEncoderAngle) {
    uint16_t nextHead = (headIdx + 1) % RING_BUFFER_SIZE;
    if (nextHead != tailIdx) {
        ringBuffer[headIdx] = { millis(), targetAngle, currentEncoderAngle };
        headIdx = nextHead;
    }
}
