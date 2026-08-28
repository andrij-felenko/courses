#include <stdint.h>
#include <stdbool.h>

// Швидкий цілочисельний квадратний корінь (Bit-by-Bit Restoration) для 64-бітних чисел
static uint32_t isqrt64(uint64_t val) {
    uint64_t b, q = 0;
    if (val == 0) return 0;
    // Початкова маска для старшого 62-го біта (парна степінь двійки)
    for (b = (uint64_t)1 << 62; b > 0; b >>= 2) {
        uint64_t t = q + b;
        q >>= 1;
        if (val >= t) {
            val -= t;
            q += b;
        }
    }
    return (uint32_t)q;
}

typedef struct {
    int32_t  x_prev;        // Попередній сирий вхід (код АЦП)
    int32_t  y_prev_q15;    // Попередній відфільтрований вихід (формат Q15)
    uint64_t sum_sq;        // 64-бітний акумулятор суми квадратів
    uint32_t sample_count;  // Кількість відліків у поточному вікні
    int32_t  alpha_q15;     // Коефіцієнт фільтра DC-Blocker (Q15)
    int16_t  hysteresis;    // Поріг гістерезису детектора нуля
    bool     armed;         // Стан детектора перетину нуля
} TrueRmsQ15;

void true_rms_q15_init(TrueRmsQ15 *ctx, int32_t alpha_q15, int16_t hysteresis) {
    ctx->x_prev = 0;
    ctx->y_prev_q15 = 0;
    ctx->sum_sq = 0;
    ctx->sample_count = 0;
    ctx->alpha_q15 = alpha_q15;
    ctx->hysteresis = hysteresis;
    ctx->armed = false;
}

// Обробка одного відліку в перериванні АЦП
// Повертає true, якщо закінчився вимірювальний період і оновлено rms_out
bool true_rms_q15_process_sample(TrueRmsQ15 *ctx, int16_t raw_adc, uint32_t *rms_out) {
    int32_t x = (int32_t)raw_adc;
    
    // IIR DC-Blocker: y[n] = x[n] - x[n-1] + α · y[n-1]
    int32_t diff = (x - ctx->x_prev) << 15;
    int32_t feedback = (int32_t)(((int64_t)ctx->alpha_q15 * ctx->y_prev_q15) >> 15);
    int32_t y_q15 = diff + feedback;
    
    ctx->x_prev = x;
    ctx->y_prev_q15 = y_q15;
    
    int32_t y_signal = y_q15 >> 15; // Повернення до масштабу коду АЦП
    
    // Накопичення квадрата (без ризику переповнення завдяки 64 бітам)
    ctx->sum_sq += (uint64_t)((int64_t)y_signal * y_signal);
    ctx->sample_count++;
    
    // Гістерезисний детектор перетину нуля (Zero-Crossing)
    if (y_signal < -ctx->hysteresis) {
        ctx->armed = true;
    } else if (ctx->armed && y_signal >= 0 && ctx->sample_count >= 100) {
        // Завершення цілого числа періодів (мінімум 100 відліків)
        uint64_t mean_sq = ctx->sum_sq / ctx->sample_count;
        *rms_out = isqrt64(mean_sq);
        
        // Скидання накопичувача для наступного вікна
        ctx->sum_sq = 0;
        ctx->sample_count = 0;
        ctx->armed = false;
        return true;
    }
    
    return false;
}
