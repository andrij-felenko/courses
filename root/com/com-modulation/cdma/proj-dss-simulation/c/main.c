#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <time.h>

#define NUM_USERS 4
#define CHIP_LEN 64
#define NUM_BITS 10000

/* Генерація матриці Адамара порядку N (N - степінь двійки) методом Сильвестра */
void generate_walsh_matrix(int n, int matrix[CHIP_LEN][CHIP_LEN]) {
    matrix[0][0] = 1;
    for (int len = 1; len < n; len *= 2) {
        for (int i = 0; i < len; i++) {
            for (int j = 0; j < len; j++) {
                matrix[i + len][j] = matrix[i][j];
                matrix[i][j + len] = matrix[i][j];
                matrix[i + len][j + len] = -matrix[i][j];
            }
        }
    }
}

/* Генерація відліку нормального шуму N(0, std_dev^2) методом Бокса-Мюллера */
double generate_gaussian_noise(double std_dev) {
    double u1 = ((double)rand() + 1.0) / ((double)RAND_MAX + 1.0);
    double u2 = ((double)rand() + 1.0) / ((double)RAND_MAX + 1.0);
    return std_dev * sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI * u2);
}

int main(void) {
    srand((unsigned int)time(NULL));

    int walsh[CHIP_LEN][CHIP_LEN];
    generate_walsh_matrix(CHIP_LEN, walsh);

    printf("=== Моделювання DSSS CDMA (C99) ===\n");
    printf("Кількість абонентів: %d, Довжина коду Волша: %d чипів\n", NUM_USERS, CHIP_LEN);
    printf("Кількість переданих бітів на користувача: %d\n\n", NUM_BITS);

    double eb_n0_db_list[] = {-4.0, -2.0, 0.0, 2.0, 4.0, 6.0};
    int num_snr_points = (int)(sizeof(eb_n0_db_list) / sizeof(eb_n0_db_list[0]));

    for (int s = 0; s < num_snr_points; s++) {
        double eb_n0_db = eb_n0_db_list[s];
        double eb_n0_linear = pow(10.0, eb_n0_db / 10.0);

        /* Розрахунок дисперсії шуму чипа */
        double noise_variance = (double)CHIP_LEN / (2.0 * eb_n0_linear);
        double noise_std_dev = sqrt(noise_variance);

        int bit_errors[NUM_USERS] = {0};

        for (int b = 0; b < NUM_BITS; b++) {
            int tx_bits[NUM_USERS];
            double tx_composite[CHIP_LEN] = {0.0};

            /* Крок 1 і 2: Генерація бітів та розширення спектра (Spreading) */
            for (int u = 0; u < NUM_USERS; u++) {
                tx_bits[u] = (rand() % 2 == 0) ? 1 : -1;
                for (int c = 0; c < CHIP_LEN; c++) {
                    tx_composite[c] += (double)(tx_bits[u] * walsh[u][c]);
                }
            }

            /* Крок 3: Передача через канал AWGN */
            double rx_composite[CHIP_LEN];
            for (int c = 0; c < CHIP_LEN; c++) {
                rx_composite[c] = tx_composite[c] + generate_gaussian_noise(noise_std_dev);
            }

            /* Крок 4: Кореляційний демодулятор (Despreading) для кожного користувача */
            for (int u = 0; u < NUM_USERS; u++) {
                double correlator_sum = 0.0;
                for (int c = 0; c < CHIP_LEN; c++) {
                    correlator_sum += rx_composite[c] * (double)walsh[u][c];
                }

                int rx_decision = (correlator_sum >= 0.0) ? 1 : -1;
                if (rx_decision != tx_bits[u]) {
                    bit_errors[u]++;
                }
            }
        }

        double total_ber = 0.0;
        for (int u = 0; u < NUM_USERS; u++) {
            total_ber += (double)bit_errors[u] / (double)NUM_BITS;
        }
        total_ber /= (double)NUM_USERS;

        printf("Eb/N0: %+5.1f дБ | Дисперсія шуму: %6.2f | Сер. BER: %8.5f (помилок: %4d)\n",
               eb_n0_db, noise_variance, total_ber, (int)(total_ber * NUM_BITS * NUM_USERS));
    }

    printf("\nМоделювання завершено успішно.\n");
    return 0;
}
