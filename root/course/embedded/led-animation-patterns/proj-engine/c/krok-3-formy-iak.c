#include <math.h>

// таблиці форм: фаза-індекс 0..255 → яскравість 0..4095
static uint16_t breatheTbl[256];   // плавне дихання (косинус)
static uint16_t easeTbl[256];      // smoothstep — живий розгін-гальмування

void buildShapeTables(void) {
    for (int i = 0; i < 256; i++) {
        float t = i / 255.0f;                       // фаза 0..1
        // дихання: (1 - cos(2πt)) / 2 → 0→1→0 за один прохід
        float b = (1.0f - cosf(t * 2.0f * (float)M_PI)) * 0.5f;
        breatheTbl[i] = (uint16_t)lroundf(b * 4095.0f);
        // smoothstep: повільно на краях, швидше всередині
        float s = t * t * (3.0f - 2.0f * t);
        easeTbl[i]   = (uint16_t)lroundf(s * 4095.0f);
    }
}

// функції форми, які кладемо в Anim.shape — лише індексація, жодного float
uint16_t shapeBreathe(uint16_t phase) { return breatheTbl[phase >> 4]; }
uint16_t shapeEase(uint16_t phase)    { return easeTbl[phase >> 4]; }
uint16_t shapeLinear(uint16_t phase)  { return phase; }            // форма = фаза
uint16_t shapeBlink(uint16_t phase)   { return (phase < 2048) ? 4095 : 0; }  // прямокутник
