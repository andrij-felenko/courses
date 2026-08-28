#include <math.h>

const float    GAMMA    = 2.2f;
const int      PWM_BITS = 12;
const uint32_t MAX_DUTY = (1u << PWM_BITS) - 1;  // 4095

// Для розуміння: формула одного значення
uint32_t gammaRuntime(uint8_t level) {
    return (uint32_t) lroundf( powf((float)level / 255.0f, GAMMA) * MAX_DUTY );
}

// Таблиця: 12 біт ≤ 4095, тобто в uint16_t (0..65535) влізає; uint8_t не підійде
uint16_t gammaLUT[256];

void buildLUT() {
    // рахуємо ОДИН раз
    for (int i = 0; i < 256; i++) {
        gammaLUT[i] = (uint16_t) gammaRuntime((uint8_t)i);
    }
}
