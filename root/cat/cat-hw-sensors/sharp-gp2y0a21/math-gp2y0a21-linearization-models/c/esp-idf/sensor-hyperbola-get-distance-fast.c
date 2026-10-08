#include <stdint.h>
#include <stddef.h>

#define HYPERBOLA_A_SCALE 21850000UL
#define HYPERBOLA_B_MV    (-148)

typedef struct {
    uint16_t voltage_mv;
    uint16_t distance_mm;
} lut_node_t;

static const lut_node_t lut_grid[] = {
    {2300, 100},
    {1650, 150},
    {1300, 200},
    {900,  300},
    {650,  400},
    {500,  600},
    {400,  800}
};
static const size_t lut_grid_size = sizeof(lut_grid) / sizeof(lut_grid[0]);

uint16_t sensor_hyperbola_get_distance_fast(uint16_t voltage_mv) {
    int32_t denominator = (int32_t)voltage_mv + HYPERBOLA_B_MV;
    if (denominator <= 0) {
        return 800;
    }
    uint32_t dist = HYPERBOLA_A_SCALE / (uint32_t)denominator;
    if (dist > 800) return 800;
    if (dist < 100) return 100;
    return (uint16_t)dist;
}

uint16_t sensor_lut_get_distance_binary(uint16_t voltage_mv) {
    if (voltage_mv >= lut_grid[0].voltage_mv) {
        return lut_grid[0].distance_mm;
    }
    if (voltage_mv <= lut_grid[lut_grid_size - 1].voltage_mv) {
        return lut_grid[lut_grid_size - 1].distance_mm;
    }

    size_t low = 0;
    size_t high = lut_grid_size - 1;

    while (high - low > 1) {
        size_t mid = low + (high - low) / 2;
        if (lut_grid[mid].voltage_mv >= voltage_mv) {
            low = mid;
        } else {
            high = mid;
        }
    }

    uint32_t v_span = lut_grid[low].voltage_mv - lut_grid[high].voltage_mv;
    uint32_t d_span = lut_grid[high].distance_mm - lut_grid[low].distance_mm;
    uint32_t v_diff = lut_grid[low].voltage_mv - voltage_mv;

    return lut_grid[low].distance_mm + (uint16_t)((v_diff * d_span) / v_span);
}
