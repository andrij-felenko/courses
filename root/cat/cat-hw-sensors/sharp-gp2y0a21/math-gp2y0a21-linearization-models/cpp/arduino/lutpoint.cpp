struct LutPoint {
    uint16_t voltage_mv;
    uint16_t distance_mm;
};

// Калібрувальна таблиця вузлів, впорядкована за спаданням напруги
static const LutPoint LUT_TABLE[] = {
    {2300, 100},
    {1650, 150},
    {1300, 200},
    {900,  300},
    {650,  400},
    {500,  600},
    {400,  800}
};
static const uint8_t LUT_SIZE = sizeof(LUT_TABLE) / sizeof(LUT_TABLE[0]);

uint16_t calculate_distance_lut(uint16_t voltage_mv) {
    if (voltage_mv >= LUT_TABLE[0].voltage_mv) {
        return LUT_TABLE[0].distance_mm;
    }
    if (voltage_mv <= LUT_TABLE[LUT_SIZE - 1].voltage_mv) {
        return LUT_TABLE[LUT_SIZE - 1].distance_mm;
    }

    for (uint8_t i = 0; i < LUT_SIZE - 1; i++) {
        if (voltage_mv <= LUT_TABLE[i].voltage_mv && voltage_mv >= LUT_TABLE[i + 1].voltage_mv) {
            uint32_t v_span = LUT_TABLE[i].voltage_mv - LUT_TABLE[i + 1].voltage_mv;
            uint32_t d_span = LUT_TABLE[i + 1].distance_mm - LUT_TABLE[i].distance_mm;
            uint32_t v_diff = LUT_TABLE[i].voltage_mv - voltage_mv;

            return LUT_TABLE[i].distance_mm + (uint16_t)((v_diff * d_span) / v_span);
        }
    }
    return 0;
}
