#include <stdint.h>
#include <stdbool.h>

/* Безпечне масштабування сирого відліку з фіксованою комою та насиченням */
int32_t scale_sensor_value_sat(int16_t raw_val, int32_t scale_q16, int32_t min_limit, int32_t max_limit) {
    /* 64-бітне множення виключає проміжне переповнення */
    int64_t intermediate = (int64_t)raw_val * scale_q16;
    
    /* Симетричне округлення та зсув з Q16.16 */
    int32_t scaled = (int32_t)((intermediate + (1LL << 15)) >> 16);
    
    /* Апаратне або програмне насичення (Saturation) */
    if (scaled > max_limit) {
        return max_limit;
    }
    if (scaled < min_limit) {
        return min_limit;
    }
    return scaled;
}
