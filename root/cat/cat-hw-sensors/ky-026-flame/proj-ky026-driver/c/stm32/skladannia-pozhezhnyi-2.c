/* ADC1 у режимі сканування двох рангів (IN0, IN1) + DMA circular; на старті —
   HAL_ADC_Start_DMA(&hadc1, (uint32_t *)adc_pair, 2), далі числа приходять самі. */
static volatile uint16_t adc_pair[2];   /* [0] — лівий канал, [1] — правий */
static float ir_l = 0, ir_r = 0;        /* згладжена сила жару зліва / справа */

static void read_sensors(void) {
    const float a = 0.15f;              /* згладжування: гасить тремтіння полумʼя */
    ir_l += a * ((float)adc_pair[0] - ir_l);
    ir_r += a * ((float)adc_pair[1] - ir_r);
}
