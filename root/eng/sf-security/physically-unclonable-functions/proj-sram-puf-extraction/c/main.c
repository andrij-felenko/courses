#include <stdio.h>
#include <stdint.h>
#include <stddef.h>

#define PUF_BLOCK_SIZE 64
#define NUM_SAMPLES 5

void sram_puf_read_raw(uint8_t *buffer, size_t len, uint32_t power_cycle_seed);
uint32_t calculate_hamming_distance(const uint8_t *buf1, const uint8_t *buf2, size_t len);
void sram_puf_majority_vote(const uint8_t samples[][PUF_BLOCK_SIZE], size_t num_samples, uint8_t *out_stable, size_t len);

int main(void) {
    uint8_t samples[NUM_SAMPLES][PUF_BLOCK_SIZE];
    uint8_t reference_puf[PUF_BLOCK_SIZE];
    uint8_t stable_puf[PUF_BLOCK_SIZE];

    printf("--- Аналіз SRAM PUF на мікроконтролері (C) ---\n");

    /* 1. Зчитування поверхового reference-відбитка під час першого включення */
    sram_puf_read_raw(reference_puf, PUF_BLOCK_SIZE, 100);

    /* 2. Серія повторних включень живлення */
    for (size_t i = 0; i < NUM_SAMPLES; i++) {
        sram_puf_read_raw(samples[i], PUF_BLOCK_SIZE, 101 + i);
        uint32_t dist = calculate_hamming_distance(reference_puf, samples[i], PUF_BLOCK_SIZE);
        double ber = (double)dist / (PUF_BLOCK_SIZE * 8) * 100.0;
        printf("[Запуск %zu] Відстань Геммінга від еталону: %u бітів (BER: %.2f%%)\n", i + 1, dist, ber);
    }

    /* 3. Мажоритарне голосування для очищення від шуму */
    sram_puf_majority_vote(samples, NUM_SAMPLES, stable_puf, PUF_BLOCK_SIZE);
    uint32_t final_dist = calculate_hamming_distance(reference_puf, stable_puf, PUF_BLOCK_SIZE);
    printf("[Мажоритарне голосування] Остаточна відстань після фільтрації: %u бітів\n", final_dist);

    return 0;
}
