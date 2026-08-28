static int32_t g_dcxo_dac_code;   /* база: центр + температурна поправка */

/* Та сама швидка петля, але ТЕПЕР готує базу, а не пише ЦАП. */
void dcxo_tick(void)
{
    int32_t T_q8 = temp_sensor_read_q8();
    int32_t dff  = dcxo_poly_q16(&g_cal, T_q8);
    uint16_t base;
    dac_status_t st = dcxo_ppb_to_dac(dff, &base);
    g_dcxo_dac_code = base;                        /* лише готуємо, НЕ пишемо */
    if (st != DAC_OK) fault_set(FAULT_TUNE_RAIL);
}
