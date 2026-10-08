typedef struct {
    uint16_t voltage_mv;
    uint16_t distance_mm;
} lut_point_t;

static const lut_point_t lut_table[] = {
    {2300, 100},
    {1650, 150},
    {1300, 200},
    {900,  300},
    {650,  400},
    {500,  600},
    {400,  800}
};
static const size_t lut_size = sizeof(lut_table) / sizeof(lut_table[0]);

uint16_t sensor_lut_get_distance(uint16_t voltage_mv) {
    if (voltage_mv >= lut_table[0].voltage_mv) {
        return lut_table[0].distance_mm;
    }
    if (voltage_mv <= lut_table[lut_size - 1].voltage_mv) {
        return lut_table[lut_size - 1].distance_mm;
    }

    for (size_t i = 0; i < lut_size - 1; i++) {
        if (voltage_mv <= lut_table[i].voltage_mv && voltage_mv >= lut_table[i + 1].voltage_mv) {
            uint32_t v_span = lut_table[i].voltage_mv - lut_table[i + 1].voltage_mv;
            uint32_t d_span = lut_table[i + 1].distance_mm - lut_table[i].distance_mm;
            uint32_t v_diff = lut_table[i].voltage_mv - voltage_mv;

            return lut_table[i].distance_mm + (uint16_t)((v_diff * d_span) / v_span);
        }
    }
    return 0;
}
