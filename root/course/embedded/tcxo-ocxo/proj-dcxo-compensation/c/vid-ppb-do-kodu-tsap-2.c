/* Викликати з таймера, скажімо 32 рази на секунду.
 * Читає давач, рахує поправку, пише ЦАП. Це ВЕСЬ DCXO —
 * поки він працює САМ, без GPS (нижче ми цей запис перенаправимо). */
static dcxo_cal_t g_cal;

void dcxo_tick(void)
{
    int32_t T_q8   = temp_sensor_read_q8();       /* давач → °C у Q8 */
    int32_t dff    = dcxo_poly_q16(&g_cal, T_q8); /* поправка, Q16 ppb */
    uint16_t code;
    dac_status_t st = dcxo_ppb_to_dac(dff, &code);

    dac_write(code);                              /* → варикап → частота */
    if (st != DAC_OK) fault_set(FAULT_TUNE_RAIL); /* упер у край — тривога */
}
