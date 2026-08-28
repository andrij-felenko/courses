// Скільки відліків усереднити в одній спробі (приглушити шум і перший
// сміттєвий відлік після ввімкнення АЦП).
#define WITNESS_SAMPLES   8u

// Усереднений відлік вузла-свідка. Перший відлік відкидаємо навмисно:
// після ввімкнення АЦП його конденсатор вибірки ще не встояний.
static uint16_t witness_average(void)
{
    (void)adc_read(CH_VREF_WITNESS);          // «прогрівний» відлік — у смітник
    uint32_t acc = 0;
    for (uint8_t i = 0; i < WITNESS_SAMPLES; ++i) {
        acc += adc_read(CH_VREF_WITNESS);
    }
    return (uint16_t)(acc / WITNESS_SAMPLES);
}
