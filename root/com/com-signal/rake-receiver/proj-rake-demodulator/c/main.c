#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>

#define CHIP_LEN 31
#define NUM_FINGERS 3
#define TOTAL_SAMPLES (CHIP_LEN + 16)

/* ПСП-послідовність (M-послідовність 31 чип) */
static const float PN_SEQ[CHIP_LEN] = {
    1, 1, 1, 1, -1, 1, -1, 1, 1, -1, -1, 1, 1, 1, -1, 1,
    -1, -1, -1, 1, -1, 1, -1, -1, 1, -1, -1, -1, -1, 1, -1
};

/* Специфікація пальця RAKE */
typedef struct {
    int delay_chips;            /* Часова затримка τ_k */
    float complex channel_h;    /* Оцінка каналу h_k = a_k * exp(j*theta_k) */
    float complex finger_out;   /* Результат обробки пальця */
} RakeFinger;

/* Очищення та зважування в окремому пальці */
static float complex process_finger(const float complex *rx_signal, int signal_len, 
                                   const RakeFinger *finger) {
    float complex corr = 0.0f + 0.0f * I;
    int tau = finger->delay_chips;

    /* Дерозширення: множення на зсунуту ПСП та інтегрування */
    for (int i = 0; i < CHIP_LEN; i++) {
        if (i + tau < signal_len) {
            corr += rx_signal[i + tau] * PN_SEQ[i];
        }
    }
    corr /= (float)CHIP_LEN;

    /* MRC ваговий коефіцієнт: w_k = conj(h_k) */
    float complex weight = conjf(finger->channel_h);

    return corr * weight;
}

int main(void) {
    /* Параметри каналу для 3 променів */
    int delays[NUM_FINGERS] = {0, 4, 9};
    float amps[NUM_FINGERS] = {0.85f, 0.55f, 0.35f};
    float phases[NUM_FINGERS] = {0.2f, 1.1f, 2.3f};

    /* Переданий інформаційний символ (+1) */
    float tx_bit = 1.0f;

    /* Моделювання вхідного сигналу r(t) */
    float complex rx_signal[TOTAL_SAMPLES] = {0};

    for (int k = 0; k < NUM_FINGERS; k++) {
        float complex h_k = amps[k] * (cosf(phases[k]) + I * sinf(phases[k]));
        int tau = delays[k];

        for (int i = 0; i < CHIP_LEN; i++) {
            rx_signal[i + tau] += tx_bit * PN_SEQ[i] * h_k;
        }
    }

    /* Додавання шуму AWGN */
    for (int i = 0; i < TOTAL_SAMPLES; i++) {
        float n_re = ((float)rand() / RAND_MAX - 0.5f) * 0.3f;
        float n_im = ((float)rand() / RAND_MAX - 0.5f) * 0.3f;
        rx_signal[i] += n_re + I * n_im;
    }

    /* Конфігурація RAKE-приймача */
    RakeFinger fingers[NUM_FINGERS];
    for (int k = 0; k < NUM_FINGERS; k++) {
        fingers[k].delay_chips = delays[k];
        /* У реальному приймачі h_k оцінюється за пілот-сигналом */
        fingers[k].channel_h = amps[k] * (cosf(phases[k]) + I * sinf(phases[k]));
    }

    /* Обробка на пальцях та MRC додавання */
    float complex total_sum = 0.0f + 0.0f * I;
    printf("=== Демодулювання пальців RAKE (C) ===\n");

    for (int k = 0; k < NUM_FINGERS; k++) {
        fingers[k].finger_out = process_finger(rx_signal, TOTAL_SAMPLES, &fingers[k]);
        total_sum += fingers[k].finger_out;

        printf("Палець %d (τ=%d): вихід = %+.3f %+.3fj (абс = %.3f)\n",
               k, fingers[k].delay_chips,
               crealf(fingers[k].finger_out), cimagf(fingers[k].finger_out),
               cabsf(fingers[k].finger_out));
    }

    /* Прийняття рішення */
    float soft_decision = crealf(total_sum);
    int detected_bit = (soft_decision > 0.0f) ? 1 : -1;

    printf("---------------------------------------\n");
    printf("Сумарний MRC сигнал: %+.3f %+.3fj\n", crealf(total_sum), cimagf(total_sum));
    printf("Детектований біт: %d (оригінал: %+d)\n", detected_bit, (int)tx_bit);

    return 0;
}
