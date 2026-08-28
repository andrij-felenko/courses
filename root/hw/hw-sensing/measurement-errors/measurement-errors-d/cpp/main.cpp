// Калібрувальна поправка офсету (виміряна на нульовому вході — еталоні).
constexpr uint16_t kAdcOffset  = 8;   // систематичний зсув, віднімаємо ОДИН раз
constexpr int      kAdcSamples = 16;  // усереднення: гасить випадковий шум у √16 = 4 рази

uint16_t read_adc_corrected() {
    uint32_t acc = 0;
    for (int i = 0; i < kAdcSamples; ++i)
        acc += adc_read_raw();                  // 16 сирих вибірок поспіль
    uint16_t avg = acc / kAdcSamples;           // середнє → розкид ±3 стиснувся до ≈ ±0.75

    // систематичний зсув НЕ гаситься усередненням — віднімаємо окремо:
    return (avg > kAdcOffset) ? (avg - kAdcOffset) : 0;
}
