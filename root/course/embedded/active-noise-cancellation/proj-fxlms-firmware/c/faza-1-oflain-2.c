#define IDENT_SAMPLES  4096       // ~0.5 с на 8 кГц — досить для 32 відводів

// викликати раз на старті; повертає 1, коли Ŝ виміряно
int identify_secondary_path(void)
{
    float err_energy = 0.0f;

    for (uint32_t n = 0; n < IDENT_SAMPLES; ++n) {
        float u = white_noise();
        dac_write(u);                       // штовхнули тест у динамік
        float d = adc_read_error_mic();     // що з нього почув мікрофон помилки
        float eps = ident_step(u, d);

        // ковзна оцінка енергії похибки (для логу / критерію зупинки)
        err_energy += 0.001f * (eps * eps - err_energy);
    }

    // err_energy тепер «полиця» — глибина моделі. Дуже велика → шлях не зловився
    // (динамік мовчить? мікрофон не той? рівень тесту нульовий?) — це сигнал не вмикати гасіння
    return (err_energy < IDENT_FAIL_LEVEL) ? 1 : 0;
}
