// ms — біжуче середнє квадратів у форматі Q (тримаємо ширше!).
// Корінь беремо лише коли рівень реально потрібен (раз на буфер), не на кожен відлік.
static uint64_t ms = 0;   // середнє квадратів, широке

void level_update(const int16_t *buf, int n) {
    for (int i = 0; i < n; i++) {
        uint64_t sq = (uint64_t)((int32_t)buf[i] * buf[i]);  // x² ≤ 32768² ≈ 1.07e9
        // ms += (sq - ms) >> 6   →   β = 1/64 (вікно ~ кілька мс при 16 кГц)
        ms += ((int64_t)sq - (int64_t)ms) >> 6;
    }
}

float level_rms(void) { return sqrtf((float)ms); }
