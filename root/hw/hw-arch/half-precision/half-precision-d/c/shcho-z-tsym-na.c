#include <stdint.h>

// Таблиця калібрування давача: 256 точок.
// У float32 — 1024 байти; у float16 — 512 байтів (удвічі менше Flash).
extern const _Float16 calib_table[256];   // лежить у Flash як 16-бітні числа

float lookup_calibrated(uint8_t index) {
    // Читаємо 16-бітне значення, рахуємо у float32:
    return (float)calib_table[index] * 1.001f + 0.5f;
}
