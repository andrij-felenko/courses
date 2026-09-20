#include <Arduino.h>

class EncoderDecoder {
private:
    volatile int32_t counter;
    uint8_t prevState;
    static const int8_t stateTable[16];

public:
    EncoderDecoder() : counter(0), prevState(0) {}

    void update(uint8_t currA, uint8_t currB) {
        uint8_t currState = (currA << 1) | currB;
        uint8_t index = (prevState << 2) | currState;
        counter += stateTable[index];
        prevState = currState;
    }

    int32_t getCount() const { return counter; }
};

const int8_t EncoderDecoder::stateTable[16] = {
    0,  1, -1,  0,
   -1,  0,  0,  1,
    1,  0,  0, -1,
    0, -1,  1,  0
};
