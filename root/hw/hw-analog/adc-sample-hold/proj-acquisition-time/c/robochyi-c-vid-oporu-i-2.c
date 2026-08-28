/* Значення тривалості набору, які РЕАЛЬНО вміє SMP-поле STM32F103,
 * у тактах шини АЦП. Мусять іти за зростанням. */
static const struct {
    double  cycles;   /* тривалість у тактах */
    uint8_t smp_code; /* код у полі SMP[2:0] */
} ADC_SMP_TABLE[] = {
    {  1.5, 0 }, {   7.5, 1 }, {  13.5, 2 }, {  28.5, 3 },
    { 41.5, 4 }, {  55.5, 5 }, {  71.5, 6 }, { 239.5, 7 },
};
#define ADC_SMP_COUNT (sizeof(ADC_SMP_TABLE) / sizeof(ADC_SMP_TABLE[0]))

/* Спеціальне значення: навіть найдовший набір замалий — потрібен буфер. */
#define ADC_SMP_NEED_BUFFER 0xFF

/* Підібрати код SMP під конкретне джерело.
 * Повертає код SMP[2:0] або ADC_SMP_NEED_BUFFER, якщо джерело
 * задобре навіть для найдовшого набору цього АЦП. */
uint8_t adc_pick_smp_code(double r_src_ohm, unsigned n_bits, double f_adc_hz)
{
    /* Параметри саме цього АЦП — з даташита STM32F103:
     * опір ключа ~1 кОм, конденсатор вибірки ~8 пФ (беремо з запасом). */
    const double R_SWITCH = 1000.0;      /* Ом  */
    const double C_HOLD   = 8.0e-12;     /* Ф   */

    const double need = adc_min_sampling_cycles(r_src_ohm, R_SWITCH,
                                                C_HOLD, n_bits, f_adc_hz);

    for (unsigned i = 0; i < ADC_SMP_COUNT; ++i)
        if (ADC_SMP_TABLE[i].cycles >= need)
            return ADC_SMP_TABLE[i].smp_code;   /* найменше, що покриває */

    return ADC_SMP_NEED_BUFFER;                 /* не вистачило й найдовшого */
}
