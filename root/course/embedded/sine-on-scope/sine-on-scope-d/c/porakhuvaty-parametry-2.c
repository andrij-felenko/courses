// Частота через підрахунок висхідних переходів рівня mean із гістерезисом.
// Повертає Гц; NAN, якщо переходів замало для оцінки.
float measure_freq(const uint16_t *buf, uint32_t n, double mean,
                   float hyst_codes, float fs)
{
    int armed = 1;                             // готові ловити висхідний перехід
    double first_cross = -1, last_cross = -1;  // індекси відліків (дробові)
    uint32_t cycles = 0;
    for (uint32_t i = 1; i < n; i++) {
        double prev = (double)buf[i-1] - mean;
        double cur  = (double)buf[i]   - mean;
        if (armed && prev < 0.0 && cur >= 0.0) {       // перетин нуля вгору
            // лінійно уточнюємо момент перетину між відліками (менша похибка)
            double frac = prev / (prev - cur);          // 0..1 між i-1 та i
            double cross = (double)(i - 1) + frac;
            if (first_cross < 0) first_cross = cross;
            else { last_cross = cross; cycles++; }
            armed = 0;                                   // гістерезис: чекаємо спаду
        } else if (cur < -(double)hyst_codes) {
            armed = 1;                                    // впали нижче −h → знову готові
        }
    }
    if (cycles == 0) return NAN;                          // менше двох переходів
    double period_samples = (last_cross - first_cross) / cycles;  // відліків на період
    return (float)(fs / period_samples);                 // Гц
}
