#include <stdint.h>
#include <stddef.h>

#define CIC_ORDER 4
#define CIC_DECIMATION 32

/* Стан 4-каскадного CIC-дециматора (N=4, R=32, M=1) */
typedef struct {
    int32_t integrators[CIC_ORDER];
    int32_t combs[CIC_ORDER];       /* Затримка z^-1 для M=1 */
    uint32_t dec_counter;
} CicDecimator;

/* Стан компенсуючого Half-Band фільтра та DC-блокера */
typedef struct {
    int32_t fir_history[16];
    size_t fir_idx;
    uint8_t fir_phase;
    int32_t dc_x_prev;
    int32_t dc_y_prev;
} AudioPostProcessor;

/* Ініціалізація структури дециматора */
void cic_init(CicDecimator *cic) {
    for (int i = 0; i < CIC_ORDER; i++) {
        cic->integrators[i] = 0;
        cic->combs[i] = 0;
    }
    cic->dec_counter = 0;
}

void post_proc_init(AudioPostProcessor *proc) {
    for (int i = 0; i < 16; i++) {
        proc->fir_history[i] = 0;
    }
    proc->fir_idx = 0;
    proc->fir_phase = 0;
    proc->dc_x_prev = 0;
    proc->dc_y_prev = 0;
}

/* Коефіцієнти 15-відвідного компенсуючого Half-Band КІХ (Q15 формат)
   Кожен парний відлік дорівнює нулю (крім центрального). */
static const int16_t FIR_COEFFS_Q15[8] = {
    -242,   /* h[0] = h[14] */
     832,   /* h[2] = h[12] */
   -2480,   /* h[4] = h[10] */
    9984,   /* h[6] = h[8]  */
   16384    /* h[7] (центр = 0.5) */
};

/* Обробка одного проміжного відліку КІХ-фільтром з децимацією на 2 */
int16_t process_halfband_and_dc(AudioPostProcessor *proc, int32_t sample_in) {
    proc->fir_history[proc->fir_idx] = sample_in;
    proc->fir_idx = (proc->fir_idx + 1) & 15;
    proc->fir_phase ^= 1;

    /* Обчислюємо вихід лише для кожного другого відліку (децимація на 2) */
    if (proc->fir_phase != 0) {
        return 0; /* Проміжний такт */
    }

    int64_t acc = 0;
    size_t idx = proc->fir_idx;

    /* Симетрична згортка Half-Band */
    acc += (int64_t)(proc->fir_history[(idx + 0) & 15] + proc->fir_history[(idx + 14) & 15]) * FIR_COEFFS_Q15[0];
    acc += (int64_t)(proc->fir_history[(idx + 2) & 15] + proc->fir_history[(idx + 12) & 15]) * FIR_COEFFS_Q15[1];
    acc += (int64_t)(proc->fir_history[(idx + 4) & 15] + proc->fir_history[(idx + 10) & 15]) * FIR_COEFFS_Q15[2];
    acc += (int64_t)(proc->fir_history[(idx + 6) & 15] + proc->fir_history[(idx + 8)  & 15]) * FIR_COEFFS_Q15[3];
    acc += (int64_t)(proc->fir_history[(idx + 7) & 15]) * FIR_COEFFS_Q15[4] * 2;

    int32_t fir_out = (int32_t)(acc >> 16);

    /* DC-блокер: y[n] = x[n] - x[n-1] + 0.995 * y[n-1] (Q15: 0.995 * 32768 = 32604) */
    int32_t dc_out = fir_out - proc->dc_x_prev + ((int64_t)proc->dc_y_prev * 32604 >> 15);
    proc->dc_x_prev = fir_out;
    proc->dc_y_prev = dc_out;

    /* Насичення до 16-бітного аудіодіапазону [-32768, 32767] */
    if (dc_out > 32767) dc_out = 32767;
    if (dc_out < -32768) dc_out = -32768;

    return (int16_t)dc_out;
}

/* Обробка буфера 32-бітних PDM слів із видачею готових PCM 48 кГц відліків */
size_t pdm_to_pcm_process(CicDecimator *cic, AudioPostProcessor *proc,
                          const uint32_t *pdm_words, size_t num_words,
                          int16_t *pcm_out) {
    size_t pcm_count = 0;

    for (size_t w = 0; w < num_words; w++) {
        uint32_t word = pdm_words[w];

        /* Обробка кожного з 32 бітів слова (старший біт надходить першим) */
        for (int bit = 31; bit >= 0; bit--) {
            int32_t bit_val = ((word >> bit) & 1) ? 1 : -1;

            /* 1. Секція інтеграторів (f_s = 3.072 МГц) */
            cic->integrators[0] += bit_val;
            cic->integrators[1] += cic->integrators[0];
            cic->integrators[2] += cic->integrators[1];
            cic->integrators[3] += cic->integrators[2];

            cic->dec_counter++;
            if (cic->dec_counter >= CIC_DECIMATION) {
                cic->dec_counter = 0;

                /* 2. Секція гребінок на проміжній частоті (f_int = 96 кГц) */
                int32_t s0 = cic->integrators[3];

                int32_t d0 = s0 - cic->combs[0];
                cic->combs[0] = s0;

                int32_t d1 = d0 - cic->combs[1];
                cic->combs[1] = d0;

                int32_t d2 = d1 - cic->combs[2];
                cic->combs[2] = d1;

                int32_t d3 = d2 - cic->combs[3];
                cic->combs[3] = d2;

                /* Масштабування виходу CIC (G_max = 32^4 = 1048576 = 2^20)
                   Зсув на 5 біт переводить 21-бітний результат у 16-бітний масштаб */
                int32_t cic_scaled = d3 >> 5;

                /* 3. Другий ступінь: Half-Band КІХ + DC блокер -> 48 кГц */
                if (proc->fir_phase == 1) {
                    pcm_out[pcm_count++] = process_halfband_and_dc(proc, cic_scaled);
                } else {
                    process_halfband_and_dc(proc, cic_scaled);
                }
            }
        }
    }
    return pcm_count;
}
