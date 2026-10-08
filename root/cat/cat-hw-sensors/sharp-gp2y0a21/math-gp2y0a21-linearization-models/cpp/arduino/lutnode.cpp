#include <Arduino.h>

// Фіксована кома: коефіцієнти гіперболічної моделі d = A / (V + B)
// A_SCALE розраховано для напруги в мВ та відстані в мм: A = 21850000, B = -148 мВ
static const uint32_t HYPERBOLA_A_SCALE = 21850000UL;
static const int32_t HYPERBOLA_B_MV = -148;

struct LutNode {
    uint16_t voltage_mv;
    uint16_t distance_mm;
};

// Калібрувальна таблиця LUT, впорядкована за спаданням напруги
static const LutNode LUT_GRID[] = {
    {2300, 100},
    {1650, 150},
    {1300, 200},
    {900,  300},
    {650,  400},
    {500,  600},
    {400,  800}
};
static const uint8_t LUT_GRID_SIZE = sizeof(LUT_GRID) / sizeof(LUT_GRID[0]);

// Цілочисельний розрахунок гіперболічної моделі
uint16_t calculate_distance_hyperbola_fast(uint16_t voltage_mv) {
    int32_t denominator = (int32_t)voltage_mv + HYPERBOLA_B_MV;
    if (denominator <= 0) {
        return 800; // Обмеження для виходу за робочу зону
    }
    uint32_t dist = HYPERBOLA_A_SCALE / (uint32_t)denominator;
    if (dist > 800) return 800;
    if (dist < 100) return 100;
    return (uint16_t)dist;
}

// Швидкий бінарний пошук інтервалу в LUT-таблиці
uint16_t calculate_distance_lut_binary(uint16_t voltage_mv) {
    if (voltage_mv >= LUT_GRID[0].voltage_mv) {
        return LUT_GRID[0].distance_mm;
    }
    if (voltage_mv <= LUT_GRID[LUT_GRID_SIZE - 1].voltage_mv) {
        return LUT_GRID[LUT_GRID_SIZE - 1].distance_mm;
    }

    uint8_t low = 0;
    uint8_t high = LUT_GRID_SIZE - 1;

    while (high - low > 1) {
        uint8_t mid = low + (high - low) / 2;
        if (LUT_GRID[mid].voltage_mv >= voltage_mv) {
            low = mid;
        } else {
            high = mid;
        }
    }

    // Лінійна інтерполяція між LUT_GRID[low] та LUT_GRID[high]
    uint32_t v_span = LUT_GRID[low].voltage_mv - LUT_GRID[high].voltage_mv;
    uint32_t d_span = LUT_GRID[high].distance_mm - LUT_GRID[low].distance_mm;
    uint32_t v_diff = LUT_GRID[low].voltage_mv - voltage_mv;

    return LUT_GRID[low].distance_mm + (uint16_t)((v_diff * d_span) / v_span);
}
