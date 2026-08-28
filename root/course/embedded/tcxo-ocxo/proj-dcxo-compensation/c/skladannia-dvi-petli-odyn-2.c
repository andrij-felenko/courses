/* Спільний запис у ЦАП: температурний feed-forward + дисципліна GPS.
 * base — код від температурної компенсації (dcxo), trim — готовий код
 * поправки від GPSDO (уже зведений до цілого в pi_step / holdover). */
void gpsdo_apply(int32_t trim)
{
    /* Температурний доданок — свіжий з швидкої петлі (глобал, оновлює dcxo_tick). */
    int32_t base = g_dcxo_dac_code;               /* центр + темп. поправка */

    int32_t code = base + trim;                   /* два внески в один код */
    dac_status_t st;
    if      (code < 0)       { code = 0;       st = DAC_RAILED_LOW;  }
    else if (code > DAC_MAX) { code = DAC_MAX; st = DAC_RAILED_HIGH; }
    else                     {                 st = DAC_OK;          }

    dac_write((uint16_t)code);
    g_last_dac_status = st;    /* цей статус читає антивіндап наступного pi_step */
}
