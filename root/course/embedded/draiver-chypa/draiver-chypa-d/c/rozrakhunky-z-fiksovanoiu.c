// C99: Цілочисельне перетворення відліків у мілігравітації (мг)
int32_t chip_raw_to_mg(int16_t raw_code, chip_range_t range) {
    int32_t sensitivity_ug; // Чутливість у мікро-g на відлік
    switch (range) {
        case CHIP_RANGE_2G:  sensitivity_ug = 61; break;  // 0.061 мг = 61 мкг
        case CHIP_RANGE_4G:  sensitivity_ug = 122; break;
        case CHIP_RANGE_8G:  sensitivity_ug = 244; break;
        case CHIP_RANGE_16G: sensitivity_ug = 732; break;
        default:             sensitivity_ug = 61; break;
    }
    
    // Проміжне множення у 64 бітах для уникнення переповнення: (raw * sensitivity_ug) / 1000
    int64_t product = (int64_t)raw_code * sensitivity_ug;
    return (int32_t)(product / 1000);
}
