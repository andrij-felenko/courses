// Один «лист-блок» каналу на схемі  →  одна функція в коді.
// Чотири екземпляри каналу  →  чотири піни АЦП у масиві.
#define N_CHAN  4
static const uint8_t CH_ADC_PIN[N_CHAN] = { 0, 1, 2, 3 };  // канали 1..4

float read_channel(uint8_t ch)          // = «дочірній лист», написаний раз
{
    uint16_t raw = adc_read(CH_ADC_PIN[ch]);   // вивід-порт цього екземпляра
    return raw * (3.3f / 4095.0f);             // код → вольти (12-бітний АЦП)
}

void scan_all(float out[N_CHAN])        // = «верхній лист»: ставить блок ×4
{
    for (uint8_t ch = 0; ch < N_CHAN; ch++)
        out[ch] = read_channel(ch);     // той самий блок, інший екземпляр
}
