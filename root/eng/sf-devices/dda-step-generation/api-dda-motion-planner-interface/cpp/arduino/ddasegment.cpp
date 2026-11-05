#include <Arduino.h>
#include <atomic>

constexpr size_t DDA_AXES = 3;
constexpr size_t DDA_BUF_SIZE = 16;

struct DdaSegment {
    uint32_t totalSteps;
    uint32_t dirMask;
    uint32_t axisDelta[DDA_AXES];
    uint32_t initialPeriodTicks;
    int32_t timerAccInc;
};

class DdaMotionPlannerInterface {
private:
    DdaSegment m_buffer[DDA_BUF_SIZE];
    std::atomic<size_t> m_head{0};
    std::atomic<size_t> m_tail{0};
    uint32_t m_accumulators[DDA_AXES];
    uint32_t m_stepCounter{0};
    uint32_t m_currentPeriod{0};

public:
    bool pushSegment(const DdaSegment& seg) {
        size_t h = m_head.load(std::memory_order_relaxed);
        size_t t = m_tail.load(std::memory_order_acquire);
        size_t nextHead = (h + 1) % DDA_BUF_SIZE;
        
        if (nextHead == t) {
            return false; // Кільцевий буфер заповнений
        }
        
        m_buffer[h] = seg;
        m_head.store(nextHead, std::memory_order_release);
        return true;
    }

    void handleInterrupt() {
        size_t t = m_tail.load(std::memory_order_relaxed);
        size_t h = m_head.load(std::memory_order_acquire);
        
        if (t == h) {
            return; // Немає нових команд
        }
        
        DdaSegment& cur = m_buffer[t];
        
        if (m_stepCounter == 0) {
            m_currentPeriod = cur.initialPeriodTicks;
            for (size_t i = 0; i < DDA_AXES; ++i) {
                m_accumulators[i] = cur.totalSteps >> 1;
            }
            digitalWrite(DIR_PIN_X, (cur.dirMask & 0x01) ? HIGH : LOW);
        }

        // Генеруємо крок провідної осі
        digitalWrite(STEP_PIN_X, HIGH);
        
        for (size_t i = 1; i < DDA_AXES; ++i) {
            m_accumulators[i] += cur.axisDelta[i];
            if (m_accumulators[i] >= cur.totalSteps) {
                m_accumulators[i] -= cur.totalSteps;
                digitalWrite(STEP_PIN_BASE + i, HIGH);
            }
        }
        
        digitalWrite(STEP_PIN_X, LOW);
        for (size_t i = 1; i < DDA_AXES; ++i) {
            digitalWrite(STEP_PIN_BASE + i, LOW);
        }

        m_stepCounter++;
        m_currentPeriod += cur.timerAccInc;
        
        if (m_stepCounter >= cur.totalSteps) {
            m_stepCounter = 0;
            size_t nextTail = (t + 1) % DDA_BUF_SIZE;
            m_tail.store(nextTail, std::memory_order_release);
        }
    }
};
