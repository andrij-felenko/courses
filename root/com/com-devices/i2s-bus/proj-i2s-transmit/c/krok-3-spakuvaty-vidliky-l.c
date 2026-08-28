#include <math.h>

// Заповнити буфер N стереовідліками синуса частотою freq_hz.
// Буфер — плаский масив int16_t: [L0, R0, L1, R1, L2, R2, ...].
// САМЕ int16_t (знаковий!): від'ємна половина хвилі — це від'ємні числа
// в доповняльному коді, а не «великі додатні».
static double phase = 0.0;   // фаза між викликами зберігається — інакше на
                             // стику буферів буде розрив хвилі → клац у звуці

void fill_sine(int16_t *buf, uint32_t frames,
               uint32_t fs, double freq_hz, double amp)
{
    double dphi = 2.0 * M_PI * freq_hz / (double)fs;   // приріст фази на відлік
    int16_t peak = (int16_t)(amp * 32767.0);           // амплітуда в шкалі int16

    for (uint32_t i = 0; i < frames; i++) {
        int16_t s = (int16_t)(peak * sin(phase));       // один знаковий відлік
        buf[2*i + 0] = s;    // лівий канал
        buf[2*i + 1] = s;    // правий канал (той самий тон в обидва вуха)
        phase += dphi;
        if (phase >= 2.0 * M_PI) phase -= 2.0 * M_PI;   // тримати фазу в межах
    }
}
