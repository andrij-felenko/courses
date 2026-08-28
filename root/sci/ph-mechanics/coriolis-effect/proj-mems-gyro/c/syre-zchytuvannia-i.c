#include <stdint.h>

// --- залежить від конкретної мікросхеми: реалізуй під свою шину (I²C/SPI) ---
// має повернути знакове 16-бітне значення осі: raw = (hi << 8) | lo
extern int16_t gyro_read_raw(int axis);
extern uint32_t millis(void);            // системний час, мс

#define AXIS_Z   2
#define G_SENS   16.4f   // LSB на (°/с) — приклад для діапазону ±2000 °/с

float gyro_rate_dps(float bias) {
    int16_t raw = gyro_read_raw(AXIS_Z);
    return (raw - bias) / G_SENS;        // (LSB − LSB) / (LSB/(°/с)) = °/с
}
