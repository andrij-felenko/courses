#include <stdint.h>
#include <math.h>

// Середньоквадратична амплітуда кадру.
// N ≈ 256 (при 16 кГц це 16 мс звуку).
float frame_rms(const int16_t *frame, int N) {
    uint64_t acc = 0;              // 16-бітний квадрат ≤ 2^30; сотні їх — треба 64 біти
    for (int i = 0; i < N; i++) {
        int32_t s = frame[i];      // розширюємо перед множенням, інакше переповнення
        acc += (uint64_t)(s * s);
    }
    return sqrtf((float)acc / (float)N);
}
