/* main.c — Приклад використання C API бібліотеки libldpc */
#include <stdio.h>
#include <stdlib.h>
#include "ldpc_codec.h"

int main(void) {
    /* Перевірочна матриця H (3x6) */
    const uint8_t h_mat[18] = {
        1, 1, 1, 0, 0, 0,
        0, 1, 0, 1, 1, 0,
        0, 0, 1, 0, 1, 1
    };

    ldpc_config_t cfg = {
        .num_v = 6,
        .num_c = 3,
        .h_matrix = h_mat,
        .algo = LDPC_ALGO_NORMALIZED_MIN_SUM,
        .max_iterations = 30,
        .norm_factor = 0.85f,
        .llr_clip_val = 15.0f
    };

    ldpc_codec_t *codec = NULL;
    ldpc_status_t st = ldpc_codec_create(&cfg, &codec);
    if (st != LDPC_SUCCESS) {
        fprintf(stderr, "Помилка створення кодека: %s\n", ldpc_status_to_string(st));
        return EXIT_FAILURE;
    }

    /* Інформаційні біти k = n - m = 6 - 3 = 3 */
    const uint8_t info_bits[3] = {1, 0, 1};
    uint8_t codeword[6] = {0};

    st = ldpc_encode(codec, info_bits, 3, codeword, 6);
    if (st != LDPC_SUCCESS) {
        fprintf(stderr, "Помилка кодування: %s\n", ldpc_status_to_string(st));
        ldpc_codec_destroy(codec);
        return EXIT_FAILURE;
    }

    /* Симуляція каналу з шумом: створення LLR (помилка у біті 1) */
    float rx_llr[6] = { -4.5f, +3.2f, -5.0f, +4.1f, +3.8f, -4.9f };

    uint8_t decoded[6] = {0};
    uint32_t iters = 0;
    st = ldpc_decode(codec, rx_llr, 6, decoded, 6, &iters);

    if (st == LDPC_SUCCESS) {
        printf("Успішне декодування за %u ітерацій!\n", iters);
        printf("Декодовані біти: ");
        for (int i = 0; i < 6; i++) {
            printf("%d ", decoded[i]);
        }
        printf("\n");
    } else {
        printf("Помилка декодування: %s\n", ldpc_status_to_string(st));
    }

    ldpc_codec_destroy(codec);
    return EXIT_SUCCESS;
}
