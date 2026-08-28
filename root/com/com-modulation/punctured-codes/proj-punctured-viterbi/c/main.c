#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Матриця виколювання для R = 3/4 (період p = 3, 2 виходи кодера)
// P[0] = {1, 1, 0}, P[1] = {1, 0, 1}
static const int PUNC_MASK_3_4[2][3] = {
    {1, 1, 0},
    {1, 0, 1}
};

// Застосування виколювання R = 3/4 до материнського потоку R = 1/2
// in_bits: масив пар бітів [v1_0, v2_0, v1_1, v2_1, ...] завдовжки 2 * n_input_bits
// out_bits: вихідний масив для передачі у канал (завдовжки (4/3) * n_input_bits)
size_t puncture_encode_3_4(const int *in_bits, size_t n_input_bits, int *out_bits) {
    size_t out_idx = 0;
    for (size_t i = 0; i < n_input_bits; i++) {
        int phase = (int)(i % 3);
        int v1 = in_bits[2 * i + 0];
        int v2 = in_bits[2 * i + 1];

        if (PUNC_MASK_3_4[0][phase]) {
            out_bits[out_idx++] = v1;
        }
        if (PUNC_MASK_3_4[1][phase]) {
            out_bits[out_idx++] = v2;
        }
    }
    return out_idx;
}

// Девіколювання на приймачі: вставляння LLR = 0.0f у місця виколотих бітів
// rx_llr: м'які вибірки з каналу (довжина n_rx_llr)
// out_llr: відновлений потік для декодера Вітербі (довжина n_input_bits * 2)
void depuncture_decode_3_4(const float *rx_llr, size_t n_input_bits, float *out_llr) {
    size_t rx_idx = 0;
    for (size_t i = 0; i < n_input_bits; i++) {
        int phase = (int)(i % 3);

        // Відновлення v1
        if (PUNC_MASK_3_4[0][phase]) {
            out_llr[2 * i + 0] = rx_llr[rx_idx++];
        } else {
            out_llr[2 * i + 0] = 0.0f; // Стирання (erasure)
        }

        // Відновлення v2
        if (PUNC_MASK_3_4[1][phase]) {
            out_llr[2 * i + 1] = rx_llr[rx_idx++];
        } else {
            out_llr[2 * i + 1] = 0.0f; // Стирання (erasure)
        }
    }
}

int main(void) {
    // 3 інформаційні біти -> 6 бітів материнського коду R=1/2 -> 4 виколоті біти R=3/4
    int mother_bits[6] = {1, 1,  1, 0,  0, 1}; // 3 пари (v1, v2)
    int punctured_bits[4];

    size_t n_punc = puncture_encode_3_4(mother_bits, 3, punctured_bits);
    printf("Виколотий потік (4 біти замість 6): ");
    for (size_t i = 0; i < n_punc; i++) {
        printf("%d ", punctured_bits[i]);
    }
    printf("\n");

    // Моделювання каналу AWGN (прості LLR значення)
    float rx_channel_llr[4] = {2.5f, 1.8f, 2.1f, -1.9f};
    float restored_viterbi_llr[6];

    depuncture_decode_3_4(rx_channel_llr, 3, restored_viterbi_llr);

    printf("Відновлений LLR потік для декодера Вітербі:\n");
    for (size_t i = 0; i < 3; i++) {
        printf("Такт %zu: v1 = %+.1f, v2 = %+.1f\n",
               i + 1, restored_viterbi_llr[2 * i], restored_viterbi_llr[2 * i + 1]);
    }

    return 0;
}
