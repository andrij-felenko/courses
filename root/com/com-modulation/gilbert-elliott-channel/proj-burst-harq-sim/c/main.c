#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define STATE_GOOD 0
#define STATE_BAD  1

#define FEC_BLOCK_DATA 4
#define FEC_BLOCK_CODE 7  /* Код Хеммінга (7, 4) */
#define FEC_CAPABILITY 1  /* Виправляє 1 помилку на блок */

/* Генератор випадкових чисел [0.0, 1.0) */
static double rand_uniform(void) {
    return (double)rand() / ((double)RAND_MAX + 1.0);
}

/* Структура стану каналу Гілберта-Елліота */
typedef struct {
    double p_gb;        /* Ймовірність G -> B */
    double p_bg;        /* Ймовірність B -> G */
    double e_g;         /* Помилка в стані G */
    double e_b;         /* Помилка в стані B */
    int current_state;  /* Поточний стан (0 = G, 1 = B) */
    
    /* Статистика */
    uint64_t total_bits;
    uint64_t total_errors;
    uint64_t bad_state_bits;
    uint64_t burst_count;
    uint64_t current_burst_len;
    uint64_t max_burst_len;
} ge_channel_t;

void ge_init(ge_channel_t *ch, double p_gb, double p_bg, double e_g, double e_b) {
    ch->p_gb = p_gb;
    ch->p_bg = p_bg;
    ch->e_g = e_g;
    ch->e_b = e_b;
    ch->current_state = STATE_GOOD;
    ch->total_bits = 0;
    ch->total_errors = 0;
    ch->bad_state_bits = 0;
    ch->burst_count = 0;
    ch->current_burst_len = 0;
    ch->max_burst_len = 0;
}

/* Передача 1 біта крізь канал */
bool ge_transmit_bit(ge_channel_t *ch, bool tx_bit, double snr_linear, double *rx_llr) {
    ch->total_bits++;
    
    /* Оновлення марковського стану */
    if (ch->current_state == STATE_GOOD) {
        if (rand_uniform() < ch->p_gb) {
            ch->current_state = STATE_BAD;
            ch->burst_count++;
            ch->current_burst_len = 1;
        }
    } else {
        ch->bad_state_bits++;
        ch->current_burst_len++;
        if (ch->current_burst_len > ch->max_burst_len) {
            ch->max_burst_len = ch->current_burst_len;
        }
        if (rand_uniform() < ch->p_bg) {
            ch->current_state = STATE_GOOD;
            ch->current_burst_len = 0;
        }
    }
    
    /* Генерація помилки залежно від поточного стану */
    double err_prob = (ch->current_state == STATE_GOOD) ? ch->e_g : ch->e_b;
    bool is_error = (rand_uniform() < err_prob);
    bool rx_bit = tx_bit ^ is_error;
    
    if (is_error) {
        ch->total_errors++;
    }
    
    /* Моделювання м'якого відліку LLR для BPSK модуляції */
    double noise_sigma = (ch->current_state == STATE_GOOD) ? 
                         1.0 / sqrt(2.0 * snr_linear) : 
                         2.5 / sqrt(2.0 * snr_linear); /* Завмирання збільшує шум */
    double s = tx_bit ? 1.0 : -1.0;
    
    /* Гауссів шум за методом Бокса-Мюллера */
    double u1 = rand_uniform() + 1e-12;
    double u2 = rand_uniform();
    double g_noise = sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI * u2) * noise_sigma;
    double y = s + g_noise;
    
    *rx_llr = 2.0 * y / (noise_sigma * noise_sigma);
    return rx_bit;
}

/* Блоковий переміжник: матриця rows (N) x cols (M) */
typedef struct {
    int rows;
    int cols;
    bool *matrix;
} interleaver_t;

interleaver_t* interleaver_create(int rows, int cols) {
    interleaver_t *it = (interleaver_t*)malloc(sizeof(interleaver_t));
    it->rows = rows;
    it->cols = cols;
    it->matrix = (bool*)calloc(rows * cols, sizeof(bool));
    return it;
}

void interleaver_free(interleaver_t *it) {
    if (it) {
        free(it->matrix);
        free(it);
    }
}

/* Запис по рядках, зчитування по стовпцях */
void interleaver_interleave(interleaver_t *it, const bool *in_data, bool *out_data) {
    for (int r = 0; r < it->rows; r++) {
        for (int c = 0; c < it->cols; c++) {
            it->matrix[r * it->cols + c] = in_data[r * it->cols + c];
        }
    }
    int out_idx = 0;
    for (int c = 0; c < it->cols; c++) {
        for (int r = 0; r < it->rows; r++) {
            out_data[out_idx++] = it->matrix[r * it->cols + c];
        }
    }
}

/* Зворотне деперемішування на приймачі */
void interleaver_deinterleave(interleaver_t *it, const bool *in_data, bool *out_data) {
    int in_idx = 0;
    for (int c = 0; c < it->cols; c++) {
        for (int r = 0; r < it->rows; r++) {
            it->matrix[r * it->cols + c] = in_data[in_idx++];
        }
    }
    for (int r = 0; r < it->rows; r++) {
        for (int c = 0; c < it->cols; c++) {
            out_data[r * it->cols + c] = it->matrix[r * it->cols + c];
        }
    }
}

/* Кодер Хеммінга (7, 4) */
void hamming74_encode(const bool d[4], bool c[7]) {
    c[0] = d[0];
    c[1] = d[1];
    c[2] = d[2];
    c[3] = d[3];
    c[4] = d[0] ^ d[1] ^ d[2];  /* Парність 1 */
    c[5] = d[1] ^ d[2] ^ d[3];  /* Парність 2 */
    c[6] = d[0] ^ d[2] ^ d[3];  /* Парність 3 */
}

/* Декодер Хеммінга (7, 4) з виправленням 1 помилки */
bool hamming74_decode(const bool r[7], bool d[4]) {
    bool s0 = r[0] ^ r[1] ^ r[2] ^ r[4];
    bool s1 = r[1] ^ r[2] ^ r[3] ^ r[5];
    bool s2 = r[0] ^ r[2] ^ r[3] ^ r[6];
    int syndrome = (s2 << 2) | (s1 << 1) | s0;
    
    bool corr[7];
    memcpy(corr, r, sizeof(corr));
    
    /* Таблиця синдромів для корекції помилок */
    if (syndrome == 5) corr[0] ^= 1;
    else if (syndrome == 3) corr[1] ^= 1;
    else if (syndrome == 7) corr[2] ^= 1;
    else if (syndrome == 6) corr[3] ^= 1;
    else if (syndrome == 1) corr[4] ^= 1;
    else if (syndrome == 2) corr[5] ^= 1;
    else if (syndrome == 4) corr[6] ^= 1;
    
    d[0] = corr[0];
    d[1] = corr[1];
    d[2] = corr[2];
    d[3] = corr[3];
    
    /* Повертає true, якщо блок успішно декодовано без залишку синдрому */
    bool re_s0 = corr[0] ^ corr[1] ^ corr[2] ^ corr[4];
    bool re_s1 = corr[1] ^ corr[2] ^ corr[3] ^ corr[5];
    bool re_s2 = corr[0] ^ corr[2] ^ corr[3] ^ corr[6];
    return (re_s0 == 0 && re_s1 == 0 && re_s2 == 0);
}

int main(void) {
    srand(42);
    
    /* Параметри моделі Гілберта-Елліота */
    double p_gb = 0.01;  /* Шанс переходу в поганий стан */
    double p_bg = 0.10;  /* Шанс виходу (сер. довжина пачки = 1/0.10 = 10 бітів) */
    double e_g = 0.0001; /* Помилка в доброму стані */
    double e_b = 0.50;   /* Помилка в поганому стані */
    double snr_db = 8.0;
    double snr_lin = pow(10.0, snr_db / 10.0);
    
    ge_channel_t channel;
    ge_init(&channel, p_gb, p_bg, e_g, e_b);
    
    int num_blocks = 10000;
    int int_depth = 16;  /* Глибина переміжника D = 16 рядків */
    interleaver_t *it = interleaver_create(int_depth, FEC_BLOCK_CODE);
    
    uint64_t raw_errors = 0;
    uint64_t fec_block_errors_no_int = 0;
    uint64_t fec_block_errors_with_int = 0;
    uint64_t harq_total_transmissions = 0;
    uint64_t harq_success_blocks = 0;
    
    printf("--- Симуляція каналу Гілберта-Елліота (P_GB=%.3f, P_BG=%.3f) ---\n", p_gb, p_bg);
    printf("Теоретична частка поганого стану pi_B: %.4f\n", p_gb / (p_gb + p_bg));
    printf("Теоретична середня довжина пачки: %.1f бітів\n\n", 1.0 / p_bg);
    
    /* Буфери даних для симуляції */
    bool *tx_frames = (bool*)malloc(num_blocks * FEC_BLOCK_DATA * sizeof(bool));
    bool *tx_coded  = (bool*)malloc(num_blocks * FEC_BLOCK_CODE * sizeof(bool));
    for (int i = 0; i < num_blocks * FEC_BLOCK_DATA; i++) {
        tx_frames[i] = rand_uniform() > 0.5;
    }
    for (int b = 0; b < num_blocks; b++) {
        hamming74_encode(&tx_frames[b * FEC_BLOCK_DATA], &tx_coded[b * FEC_BLOCK_CODE]);
    }
    
    /* 1. Дослідження FEC БЕЗ перемішування */
    for (int b = 0; b < num_blocks; b++) {
        bool rx_block[FEC_BLOCK_CODE];
        double llr;
        for (int i = 0; i < FEC_BLOCK_CODE; i++) {
            rx_block[i] = ge_transmit_bit(&channel, tx_coded[b * FEC_BLOCK_CODE + i], snr_lin, &llr);
        }
        bool dec_data[FEC_BLOCK_DATA];
        hamming74_decode(rx_block, dec_data);
        if (memcmp(dec_data, &tx_frames[b * FEC_BLOCK_DATA], FEC_BLOCK_DATA * sizeof(bool)) != 0) {
            fec_block_errors_no_int++;
        }
    }
    
    /* 2. Дослідження FEC З перемішуванням (пакети по int_depth блоків) */
    ge_init(&channel, p_gb, p_bg, e_g, e_b);
    int groups = num_blocks / int_depth;
    bool *int_in  = (bool*)malloc(int_depth * FEC_BLOCK_CODE * sizeof(bool));
    bool *int_out = (bool*)malloc(int_depth * FEC_BLOCK_CODE * sizeof(bool));
    bool *rx_int  = (bool*)malloc(int_depth * FEC_BLOCK_CODE * sizeof(bool));
    bool *rx_deint = (bool*)malloc(int_depth * FEC_BLOCK_CODE * sizeof(bool));
    
    for (int g = 0; g < groups; g++) {
        memcpy(int_in, &tx_coded[g * int_depth * FEC_BLOCK_CODE], int_depth * FEC_BLOCK_CODE * sizeof(bool));
        interleaver_interleave(it, int_in, int_out);
        
        double llr;
        for (int i = 0; i < int_depth * FEC_BLOCK_CODE; i++) {
            rx_int[i] = ge_transmit_bit(&channel, int_out[i], snr_lin, &llr);
        }
        interleaver_deinterleave(it, rx_int, rx_deint);
        
        for (int b = 0; b < int_depth; b++) {
            bool dec_data[FEC_BLOCK_DATA];
            hamming74_decode(&rx_deint[b * FEC_BLOCK_CODE], dec_data);
            if (memcmp(dec_data, &tx_frames[(g * int_depth + b) * FEC_BLOCK_DATA], FEC_BLOCK_DATA * sizeof(bool)) != 0) {
                fec_block_errors_with_int++;
            }
        }
    }
    
    /* 3. Дослідження Chase Combining HARQ */
    ge_init(&channel, p_gb, p_bg, e_g, e_b);
    for (int b = 0; b < num_blocks; b++) {
        double accumulated_llr[FEC_BLOCK_CODE] = {0};
        bool decoded_ok = false;
        int max_retries = 4;
        
        for (int attempt = 0; attempt < max_retries && !decoded_ok; attempt++) {
            harq_total_transmissions++;
            bool rx_hard[FEC_BLOCK_CODE];
            
            for (int i = 0; i < FEC_BLOCK_CODE; i++) {
                double new_llr;
                ge_transmit_bit(&channel, tx_coded[b * FEC_BLOCK_CODE + i], snr_lin, &new_llr);
                accumulated_llr[i] += new_llr;  /* М'яке об'єднання LLR */
                rx_hard[i] = (accumulated_llr[i] > 0.0);
            }
            
            bool dec_data[FEC_BLOCK_DATA];
            bool no_syndrome = hamming74_decode(rx_hard, dec_data);
            if (no_syndrome && memcmp(dec_data, &tx_frames[b * FEC_BLOCK_DATA], FEC_BLOCK_DATA * sizeof(bool)) == 0) {
                decoded_ok = true;
                harq_success_blocks++;
            }
        }
    }
    
    printf("Емпірична середня довжина пачки: %.2f бітів\n", 
           channel.burst_count ? (double)channel.bad_state_bits / channel.burst_count : 0.0);
    printf("Максимальна довжина пачки зафіксована: %llu бітів\n\n", (unsigned long long)channel.max_burst_len);
    
    printf("--- Результати роботи системи захисту від помилок ---\n");
    printf("1. FEC без перемішування (BLER):       %.4e (%llu помилок)\n",
           (double)fec_block_errors_no_int / num_blocks, (unsigned long long)fec_block_errors_no_int);
    printf("2. FEC з перемішуванням D=%d (BLER):    %.4e (%llu помилок)\n",
           int_depth, (double)fec_block_errors_with_int / (groups * int_depth), (unsigned long long)fec_block_errors_with_int);
    printf("3. HARQ Chase Combining (Успішність):  %.2f%% (Сер. кількість спроб: %.2f)\n",
           100.0 * (double)harq_success_blocks / num_blocks, (double)harq_total_transmissions / num_blocks);
    
    /* Звільнення пам'яті */
    interleaver_free(it);
    free(tx_frames);
    free(tx_coded);
    free(int_in);
    free(int_out);
    free(rx_int);
    free(rx_deint);
    return 0;
}
