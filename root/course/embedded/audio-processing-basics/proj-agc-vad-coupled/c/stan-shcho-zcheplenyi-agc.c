#include <stdint.h>
#include <stdbool.h>

typedef struct {
    // ── ядро AGC (як у темі) ──
    float    gain;         // поточне підсилення (лінійне)
    float    target;       // цільовий RMS
    float    a_atk;        // коефіцієнт EMA для атаки  (з часу атаки)
    float    a_rel;        // коефіцієнт EMA для відпускання (з часу відпускання)
    float    max_gain;     // стеля проти витягування шуму
    // ── зчеплення з VAD ──
    uint16_t hold_frames;  // тривалість утримання, кадрів (з часу hold)
    uint16_t hold;         // лічильник утримання, що лишився
    float    gate_level;   // шумовий поріг: нижче нього не піднімати підсилення
    bool     frozen;       // поточний режим: true = підсилення заморожене
} agc_vad_t;
