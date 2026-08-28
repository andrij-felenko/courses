// Усічене середнє: відкинути по `trim` відліків з кожного краю, усереднити решту.
// Поєднує стійкість медіани до викидів із гладкістю середнього.
uint16_t adc_read_trimmed_mean(uint8_t channel, uint16_t *scratch,
                               unsigned n, unsigned trim) {
    for (unsigned i = 0; i < n; i++) scratch[i] = adc_read_raw(channel);
    qsort(scratch, n, sizeof(scratch[0]), cmp_u16);

    if (2 * trim >= n) return scratch[n / 2];   // зрізали б усе — впади до медіани
    uint32_t acc = 0;
    for (unsigned i = trim; i < n - trim; i++) acc += scratch[i];
    return (uint16_t)(acc / (n - 2 * trim));
}
