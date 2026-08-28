// пасивний баланс: зливаємо найповнішу комірку, поки розрив > порога
void balance_step(const uint16_t v_mV[], uint8_t n) {
    uint8_t hi = 0, lo = 0;                 // індекси макс. і мін. напруги
    for (uint8_t i = 1; i < n; i++) {
        if (v_mV[i] > v_mV[hi]) hi = i;
        if (v_mV[i] < v_mV[lo]) lo = i;
    }
    uint16_t spread = v_mV[hi] - v_mV[lo];  // розкид по пакету, мВ
    for (uint8_t i = 0; i < n; i++)
        bleed_set(i, false);                // спершу всі ключі вимкнути
    if (spread > BALANCE_THRESH_MV)         // напр., 20 мВ
        bleed_set(hi, true);                // лише найповнішу — на розрядний резистор
}
