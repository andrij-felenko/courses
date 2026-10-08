#include <stdint.h>
#include <stdbool.h>

typedef enum {
    RANGE_OK = 0,
    RANGE_BLIND_ZONE,
    RANGE_TOO_FAR
} range_status_t;

typedef struct {
    uint16_t voltage_mv;
    uint16_t distance_mm;
} lut_node_t;

// Калібрувальна таблиця LUT (11 опорних вузлів від 100 мм до 800 мм)
static const lut_node_t GP2Y0A21_LUT[] = {
    {3100, 100},
    {2500, 120},
    {2000, 150},
    {1550, 200},
    {1250, 250},
    {1050, 300},
    {800,  400},
    {650,  500},
    {520,  600},
    {450,  700},
    {400,  800}
};

#define LUT_SIZE (sizeof(GP2Y0A21_LUT) / sizeof(GP2Y0A21_LUT[0]))

range_status_t gp2y0a21_calculate_distance_lut(uint16_t voltage_mv, uint16_t *out_distance_mm) {
    // 1. Перевірка сліпої зони (< 10 см)
    if (voltage_mv > GP2Y0A21_LUT[0].voltage_mv) {
        *out_distance_mm = GP2Y0A21_LUT[0].distance_mm;
        return RANGE_BLIND_ZONE;
    }
    
    // 2. Перевірка виходу за дальню межу (> 80 см)
    if (voltage_mv < GP2Y0A21_LUT[LUT_SIZE - 1].voltage_mv) {
        *out_distance_mm = GP2Y0A21_LUT[LUT_SIZE - 1].distance_mm;
        return RANGE_TOO_FAR;
    }

    // 3. Пошук інтервалу в таблиці LUT
    for (size_t i = 0; i < LUT_SIZE - 1; i++) {
        if (voltage_mv <= GP2Y0A21_LUT[i].voltage_mv && 
            voltage_mv >= GP2Y0A21_LUT[i + 1].voltage_mv) {
            
            uint32_t v1 = GP2Y0A21_LUT[i].voltage_mv;
            uint32_t v2 = GP2Y0A21_LUT[i + 1].voltage_mv;
            uint32_t d1 = GP2Y0A21_LUT[i].distance_mm;
            uint32_t d2 = GP2Y0A21_LUT[i + 1].distance_mm;

            // Кусково-лінійна інтерполяція в цілих числах
            // d = d1 + (voltage_mv - v1) * (d2 - d1) / (v2 - v1)
            int32_t dist = d1 + ((int32_t)(voltage_mv - v1) * (int32_t)(d2 - d1)) / (int32_t)(v2 - v1);
            *out_distance_mm = (uint16_t)dist;
            return RANGE_OK;
        }
    }

    return RANGE_TOO_FAR;
}
