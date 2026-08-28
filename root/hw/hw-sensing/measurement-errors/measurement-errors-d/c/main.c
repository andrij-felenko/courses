// Калібрувальна поправка офсету (виміряна на нульовому вході — еталоні).
#define ADC_OFFSET   8        // систематичний зсув, віднімаємо ОДИН раз
#define ADC_SAMPLES  16       // усереднення: гасить випадковий шум у √16 = 4 рази

uint16_t read_adc_corrected(void) {
    uint32_t acc = 0;
    for (int i = 0; i < ADC_SAMPLES; i++)
        acc += adc_read_raw();         // 16 сирих вибірок поспіль
    uint16_t avg = acc / ADC_SAMPLES;  // середнє → розкид ±3 стиснувся до ≈ ±0.75

    // систематичний зсув НЕ гаситься усередненням — віднімаємо окремо:
    return (avg > ADC_OFFSET) ? (avg - ADC_OFFSET) : 0;
}
