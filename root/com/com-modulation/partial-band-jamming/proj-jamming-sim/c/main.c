#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>
#include <time.h>

#define NUM_CHANNELS 64
#define TOTAL_BITS 24000
#define INTERLEAVER_ROWS 8
#define INTERLEAVER_COLS 9

// Генерація нормального гаусового шуму за перетворенням Бокса-Мюллера
static double generate_gaussian(double mean, double stddev) {
    double u1 = (double)rand() / RAND_MAX;
    double u2 = (double)rand() / RAND_MAX;
    if (u1 < 1e-10) u1 = 1e-10;
    double z0 = sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI * u2);
    return mean + stddev * z0;
}

// Моделювання некогерентного детектора BFSK у каналі із завадою
static bool transmit_bfsk_symbol(bool bit, bool is_jammed, double clean_snr_lin, double jam_snr_lin) {
    double snr_lin = is_jammed ? jam_snr_lin : clean_snr_lin;
    double signal_amp = sqrt(snr_lin);
    double sigma = 1.0;

    // Квадратурний демодулятор каналу 0 (частота f0)
    double r0_i = (bit == 0 ? signal_amp : 0.0) + generate_gaussian(0.0, sigma);
    double r0_q = generate_gaussian(0.0, sigma);
    double energy0 = r0_i * r0_i + r0_q * r0_q;

    // Квадратурний демодулятор каналу 1 (частота f1)
    double r1_i = (bit == 1 ? signal_amp : 0.0) + generate_gaussian(0.0, sigma);
    double r1_q = generate_gaussian(0.0, sigma);
    double energy1 = r1_i * r1_i + r1_q * r1_q;

    return (energy1 > energy0);
}

// Блоковий перемішувач бітів (Matrix Interleaver)
static void interleave(const bool *in, bool *out, int size, int rows, int cols) {
    int block_size = rows * cols;
    int num_blocks = size / block_size;
    for (int b = 0; b < num_blocks; ++b) {
        int offset = b * block_size;
        for (int r = 0; r < rows; ++r) {
            for (int c = 0; c < cols; ++c) {
                out[offset + c * rows + r] = in[offset + r * cols + c];
            }
        }
    }
}

// Блоковий деперемішувач бітів (Matrix Deinterleaver)
static void deinterleave(const bool *in, bool *out, int size, int rows, int cols) {
    int block_size = rows * cols;
    int num_blocks = size / block_size;
    for (int b = 0; b < num_blocks; ++b) {
        int offset = b * block_size;
        for (int r = 0; r < rows; ++r) {
            for (int c = 0; c < cols; ++c) {
                out[offset + r * cols + c] = in[offset + c * rows + r];
            }
        }
    }
}

int main(void) {
    srand(1337); // Фіксована ініціалізація для відтворюваності результатів

    double clean_snr_db = 15.0; // SNR чистих каналів (+15 дБ)
    double jam_snr_db = -3.0;   // SNR глушених каналів (-3 дБ)
    double rho = 0.20;          // Завада покриває 20% смуги (13 з 64 каналів)

    double clean_snr_lin = pow(10.0, clean_snr_db / 10.0);
    double jam_snr_lin = pow(10.0, jam_snr_db / 10.0);
    int jammed_channels = (int)(NUM_CHANNELS * rho);

    bool *tx_bits = (bool *)malloc(TOTAL_BITS * sizeof(bool));
    bool *rx_bits_uncoded = (bool *)malloc(TOTAL_BITS * sizeof(bool));

    for (int i = 0; i < TOTAL_BITS; ++i) {
        tx_bits[i] = rand() % 2;
    }

    // 1. Симуляція некодованої передачі FHSS
    int errors_uncoded = 0;
    for (int i = 0; i < TOTAL_BITS; ++i) {
        int channel = rand() % NUM_CHANNELS;
        bool is_jammed = (channel < jammed_channels);
        rx_bits_uncoded[i] = transmit_bfsk_symbol(tx_bits[i], is_jammed, clean_snr_lin, jam_snr_lin);
        if (rx_bits_uncoded[i] != tx_bits[i]) {
            errors_uncoded++;
        }
    }

    // 2. Симуляція кодованої передачі з повторенням (3x) та перемішуванням
    int code_len = TOTAL_BITS * 3;
    bool *coded_bits = (bool *)malloc(code_len * sizeof(bool));
    bool *interleaved_bits = (bool *)malloc(code_len * sizeof(bool));
    bool *rx_interleaved = (bool *)malloc(code_len * sizeof(bool));
    bool *rx_coded = (bool *)malloc(code_len * sizeof(bool));

    // Потрійне повторення (Repetition Code R=1/3)
    for (int i = 0; i < TOTAL_BITS; ++i) {
        coded_bits[3 * i]     = tx_bits[i];
        coded_bits[3 * i + 1] = tx_bits[i];
        coded_bits[3 * i + 2] = tx_bits[i];
    }

    // Перемішування бітів
    interleave(coded_bits, interleaved_bits, code_len, INTERLEAVER_ROWS, INTERLEAVER_COLS);

    // Передача крізь FHSS канал із завадою
    for (int i = 0; i < code_len; ++i) {
        int channel = rand() % NUM_CHANNELS;
        bool is_jammed = (channel < jammed_channels);
        rx_interleaved[i] = transmit_bfsk_symbol(interleaved_bits[i], is_jammed, clean_snr_lin, jam_snr_lin);
    }

    // Деперемішування бітів
    deinterleave(rx_interleaved, rx_coded, code_len, INTERLEAVER_ROWS, INTERLEAVER_COLS);

    // Мажоритарне декодування
    int errors_coded = 0;
    for (int i = 0; i < TOTAL_BITS; ++i) {
        int sum = rx_coded[3 * i] + rx_coded[3 * i + 1] + rx_coded[3 * i + 2];
        bool decoded_bit = (sum >= 2);
        if (decoded_bit != tx_bits[i]) {
            errors_coded++;
        }
    }

    printf("=== Результати симуляції частково-смугової завади (C) ===\n");
    printf("Всього бітів: %d, Каналів: %d, Частка завади rho: %.2f\n", TOTAL_BITS, NUM_CHANNELS, rho);
    printf("BER некодованої передачі під PBJ: %.5f (%d помилок)\n", (double)errors_uncoded / TOTAL_BITS, errors_uncoded);
    printf("BER кодованої передачі (Code+Interleaving) під PBJ: %.5f (%d помилок)\n", (double)errors_coded / TOTAL_BITS, errors_coded);

    free(tx_bits);
    free(rx_bits_uncoded);
    free(coded_bits);
    free(interleaved_bits);
    free(rx_interleaved);
    free(rx_coded);

    return 0;
}
