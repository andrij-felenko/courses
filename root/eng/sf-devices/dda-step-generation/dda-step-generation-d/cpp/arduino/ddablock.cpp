#include <Arduino.h>
#include <atomic>

constexpr uint8_t AXIS_COUNT = 3;
constexpr uint8_t RING_BUFFER_SIZE = 16;

struct DdaBlock {
    uint32_t stepCountLeading;
    uint32_t stepIncrement[AXIS_COUNT];
    uint8_t dirMask;
    uint32_t timerTicksPerStep;
};

class DdaRingBuffer {
public:
    DdaRingBuffer() : head(0), tail(0) {}

    bool push(const DdaBlock& block) {
        size_t currentHead = head.load(std::memory_order_relaxed);
        size_t nextHead = (currentHead + 1) % RING_BUFFER_SIZE;
        if (nextHead == tail.load(std::memory_order_acquire)) {
            return false; // Буфер переповнено
        }
        buffer[currentHead] = block;
        head.store(nextHead, std::memory_order_release);
        return true;
    }

    bool pop(DdaBlock& block) {
        size_t currentTail = tail.load(std::memory_order_relaxed);
        if (currentTail == head.load(std::memory_order_acquire)) {
            return false; // Буфер порожній
        }
        block = buffer[currentTail];
        tail.store((currentTail + 1) % RING_BUFFER_SIZE, std::memory_order_release);
        return true;
    }

private:
    DdaBlock buffer[RING_BUFFER_SIZE];
    std::atomic<size_t> head;
    std::atomic<size_t> tail;
};

static DdaRingBuffer motionQueue;
static uint32_t accumulators[AXIS_COUNT] = {0};
static uint32_t stepCounter = 0;
static DdaBlock currentBlock;
static bool blockActive = false;

const uint8_t STEP_PINS[AXIS_COUNT] = {2, 4, 12};
const uint8_t DIR_PINS[AXIS_COUNT]  = {3, 5, 13};

// Переривання таймера для крокового генератора
void IRAM_ATTR onDdaTimerTick() {
    for (uint8_t i = 0; i < AXIS_COUNT; i++) {
        digitalWrite(STEP_PINS[i], LOW);
    }

    if (!blockActive) {
        if (motionQueue.pop(currentBlock)) {
            for (uint8_t i = 0; i < AXIS_COUNT; i++) {
                digitalWrite(DIR_PINS[i], (currentBlock.dirMask >> i) & 0x01);
                accumulators[i] = 0;
            }
            stepCounter = 0;
            blockActive = true;
        } else {
            return;
        }
    }

    for (uint8_t i = 0; i < AXIS_COUNT; i++) {
        uint32_t oldAcc = accumulators[i];
        accumulators[i] += currentBlock.stepIncrement[i];

        if (accumulators[i] < oldAcc) {
            digitalWrite(STEP_PINS[i], HIGH);
        }
    }

    stepCounter++;
    if (stepCounter >= currentBlock.stepCountLeading) {
        blockActive = false;
    }
}
