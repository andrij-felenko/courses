#include <stdint.h>

// axis_to_us — з базової теми: команда −1..+1 → ширина 1000..2000 мкс.
uint16_t axis_to_us(float cmd, int reverse, int trim_us) {
    if (reverse) cmd = -cmd;
    if (cmd < -1.0f) cmd = -1.0f;
    if (cmd >  1.0f) cmd =  1.0f;
    int us = 1500 + trim_us + (int)(cmd * 500.0f);
    if (us < 1000) us = 1000;
    if (us > 2000) us = 2000;
    return (uint16_t)us;
}

static float expo(float x, float e) { return e*x*x*x + (1.0f-e)*x; }

// Елевони з кривими та пріоритетним насиченням (крен важливіший за тангаж).
void elevon_pipeline(float roll, float pitch,
                     float rate, float e,
                     uint16_t *left_us, uint16_t *right_us) {
    // 1) криві: спершу expo (м'який центр), тоді rate (звузити хід)
    roll  = expo(roll,  e) * rate;
    pitch = expo(pitch, e) * rate;

    // 2) пріоритет: крен бере хід першим; тангажу лишається (1 − |roll|)
    float head = 1.0f - (roll < 0 ? -roll : roll);   // скільки ходу лишилось
    if (head < 0.0f) head = 0.0f;
    if (pitch >  head) pitch =  head;                // тангаж не краде крен
    if (pitch < -head) pitch = -head;

    // 3) мікс елевонів: рядки матриці M
    float left  = pitch + roll;                      // [ +1 +1 ]
    float right = pitch - roll;                      // [ -1 +1 ]

    // 4) доведення кожного виходу (права поверхня дзеркальна → реверс)
    *left_us  = axis_to_us(left,  0, 0);
    *right_us = axis_to_us(right, 1, 0);
}
