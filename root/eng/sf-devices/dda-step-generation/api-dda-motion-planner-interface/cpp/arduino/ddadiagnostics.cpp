#include <Arduino.h>

class DdaDiagnostics {
private:
    uint8_t m_debugPin;
    uint32_t m_underrunCount{0};
    uint32_t m_maxExecutionTimeMicros{0};

public:
    explicit DdaDiagnostics(uint8_t debugPin) : m_debugPin(debugPin) {}

    void init() {
        pinMode(m_debugPin, OUTPUT);
        digitalWrite(m_debugPin, LOW);
    }

    inline void startIsrProfiling() const {
        digitalWrite(m_debugPin, HIGH);
    }

    inline void stopIsrProfiling() const {
        digitalWrite(m_debugPin, LOW);
    }

    void recordUnderrun() {
        m_underrunCount++;
    }

    uint32_t getUnderrunCount() const {
        return m_underrunCount;
    }

    void handleEmergencyStop(std::atomic<size_t>& head, std::atomic<size_t>& tail) {
        // Атомарне очищення кільцевого буфера
        size_t currentHead = head.load(std::memory_order_relaxed);
        tail.store(currentHead, std::memory_order_release);
        recordUnderrun();
    }
};
