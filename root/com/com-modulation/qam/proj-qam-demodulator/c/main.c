#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define M_PI_VAL 3.14159265358979323846

/* Структура комплексного символу I/Q */
typedef struct {
    double i;
    double q;
} qam_symbol_t;

/* Генератор шуму Бокса-Мюллера */
static double generate_gaussian_noise(double sigma) {
    double u1 = (double)rand() / (RAND_MAX + 1.0);
    double u2 = (double)rand() / (RAND_MAX + 1.0);
    if (u1 < 1e-12) u1 = 1e-12;
    return sigma * sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI_VAL * u2);
}

/* 1D Грей мапування для 2 бітів -> 4-PAM {-3, -1, +1, +3} */
static double gray_map_2bit(uint8_t bits_2bit) {
    switch (bits_2bit & 0x03) {
        case 0: return -3.0; /* 00 */
        case 1: return -1.0; /* 01 */
        case 3: return  1.0; /* 11 */
        case 2: return  3.0; /* 10 */
        default: return 0.0;
    }
}

/* 1D Грей демодулювання для 4-PAM */
static uint8_t gray_demap_2bit(double val) {
    if (val < -2.0)     return 0; /* 00 */
    else if (val < 0.0) return 1; /* 01 */
    else if (val < 2.0) return 3; /* 11 */
    else                return 2; /* 10 */
}

/* Модулятор 16-QAM: упаковує масив бітів у масив комплексних символів */
void mod_16qam(const uint8_t *bits, size_t num_bits, qam_symbol_t *symbols) {
    const double norm = 1.0 / sqrt(10.0); /* E_avg = 1.0 */
    size_t num_symbols = num_bits / 4;
    
    for (size_t k = 0; k < num_symbols; k++) {
        uint8_t b_i = (bits[4 * k + 0] << 1) | bits[4 * k + 1];
        uint8_t b_q = (bits[4 * k + 2] << 1) | bits[4 * k + 3];
        
        symbols[k].i = gray_map_2bit(b_i) * norm;
        symbols[k].q = gray_map_2bit(b_q) * norm;
    }
}

/* Жорсткий демодулятор 16-QAM */
void demap_16qam_hard(const qam_symbol_t *symbols, size_t num_symbols, uint8_t *bits_out) {
    const double scale = sqrt(10.0);
    
    for (size_t k = 0; k < num_symbols; k++) {
        double val_i = symbols[k].i * scale;
        double val_q = symbols[k].q * scale;
        
        uint8_t b_i = gray_demap_2bit(val_i);
        uint8_t b_q = gray_demap_2bit(val_q);
        
        bits_out[4 * k + 0] = (b_i >> 1) & 0x01;
        bits_out[4 * k + 1] = (b_i >> 0) & 0x01;
        bits_out[4 * k + 2] = (b_q >> 1) & 0x01;
        bits_out[4 * k + 3] = (b_q >> 0) & 0x01;
    }
}

/* М'який демодулятор 16-QAM (Max-Log LLR) */
void demap_16qam_soft(const qam_symbol_t *symbols, size_t num_symbols, double n0, double *llrs_out) {
    const double norm = 1.0 / sqrt(10.0);
    const double d = 2.0 * norm;
    const double factor = 2.0 * d / (n0 / 2.0); /* 4d / N0 */

    for (size_t k = 0; k < num_symbols; k++) {
        double yi = symbols[k].i;
        double yq = symbols[k].q;
        
        /* LLR для бітів I */
        llrs_out[4 * k + 0] = factor * yi;
        llrs_out[4 * k + 1] = factor * (d - fabs(yi));
        
        /* LLR для бітів Q */
        llrs_out[4 * k + 2] = factor * yq;
        llrs_out[4 * k + 3] = factor * (d - fabs(yq));
    }
}

int main(void) {
    const size_t num_bits = 40000;
    const size_t num_symbols = num_bits / 4;
    
    uint8_t *tx_bits = (uint8_t *)malloc(num_bits * sizeof(uint8_t));
    uint8_t *rx_bits = (uint8_t *)malloc(num_bits * sizeof(uint8_t));
    qam_symbol_t *tx_syms = (qam_symbol_t *)malloc(num_symbols * sizeof(qam_symbol_t));
    qam_symbol_t *rx_syms = (qam_symbol_t *)malloc(num_symbols * sizeof(qam_symbol_t));
    double *llrs = (double *)malloc(num_bits * sizeof(double));

    for (size_t i = 0; i < num_bits; i++) {
        tx_bits[i] = rand() % 2;
    }

    mod_16qam(tx_bits, num_bits, tx_syms);

    printf("=== Симуляція 16-QAM модему (Monte Carlo) ===\n");
    printf("Eb/N0 (дБ) | BER (Hard)  | BER (Soft Sign)\n");
    printf("-------------------------------------------\n");

    for (double ebn0_db = 0.0; ebn0_db <= 12.0; ebn0_db += 2.0) {
        double ebn0_lin = pow(10.0, ebn0_db / 10.0);
        double k = 4.0; /* 16-QAM */
        double esn0_lin = k * ebn0_lin;
        double n0 = 1.0 / esn0_lin;
        double sigma = sqrt(n0 / 2.0);

        /* Додавання AWGN */
        for (size_t i = 0; i < num_symbols; i++) {
            rx_syms[i].i = tx_syms[i].i + generate_gaussian_noise(sigma);
            rx_syms[i].q = tx_syms[i].q + generate_gaussian_noise(sigma);
        }

        /* Жорстка та м'яка демодуляція */
        demap_16qam_hard(rx_syms, num_symbols, rx_bits);
        demap_16qam_soft(rx_syms, num_symbols, n0, llrs);

        size_t hard_errors = 0;
        size_t soft_errors = 0;
        for (size_t i = 0; i < num_bits; i++) {
            if (rx_bits[i] != tx_bits[i]) hard_errors++;
            uint8_t soft_bit = (llrs[i] >= 0.0) ? 1 : 0;
            if (soft_bit != tx_bits[i]) soft_errors++;
        }

        printf(" %4.1f дБ   | %1.5f     | %1.5f\n",
               ebn0_db, (double)hard_errors / num_bits, (double)soft_errors / num_bits);
    }

    free(tx_bits); free(rx_bits); free(tx_syms); free(rx_syms); free(llrs);
    return 0;
}
