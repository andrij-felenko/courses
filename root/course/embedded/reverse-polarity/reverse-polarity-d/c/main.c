/* Поріг у одиницях АЦП (12-bit, опорна 3.3 В, дільник 1:11 -> шкала ~36 В). */
#define ADC_FULL      4095u
#define VREF_MV       3300u
#define DIV_NUM       11u          /* (R1+R2)/R2 */
#define VBUS_MIN_MV   4500u        /* нижче — живлення нездорове */
#define VBUS_NOM_MV   5000u

static uint32_t adc_to_mv_bus(uint16_t raw)
{
    /* мВ на вході дільника = raw/FULL * VREF * DIV */
    return (uint32_t)raw * VREF_MV / ADC_FULL * DIV_NUM;
}

void power_watchdog(void)
{
    uint16_t raw = adc_read(ADC_CH_VBUS);
    uint32_t vbus = adc_to_mv_bus(raw);

    if (vbus < VBUS_MIN_MV) {
        /* Живлення просіло: або недовідкритий FET (body-діод),
           або аварія. Рятуємо стан і скидаємо навантаження. */
        flush_state_to_nvm();          /* зберегти критичне у флеш/FRAM */
        load_disable();                /* зняти важке навантаження */
        fault_flag_set(FAULT_UNDERVOLT);
    }
}
