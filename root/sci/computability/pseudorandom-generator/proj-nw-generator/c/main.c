#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

#define NW_SEED_LEN 16   /* Довжина вхідного насіння d у бітах */
#define NW_SUBSET_LEN 6  /* Розмір підмножини l у бітах */
#define NW_OUT_LEN 32    /* Кількість згенерованих бітів m */
#define NW_MAX_INTERSECT 2 /* Максимальний перетин підмножин gamma */

/* Структура комбінаторного дизайну */
typedef struct {
    size_t seed_len;
    size_t subset_len;
    size_t out_len;
    uint8_t design[NW_OUT_LEN][NW_SUBSET_LEN];
} nw_design_t;

/* Обчислення базової складної булевої функції f(x) від l бітів */
static uint8_t nw_hard_function(uint32_t x_bits, size_t l) {
    /* Нелінійна комбінація парності та кон'юнкцій змінних */
    uint8_t parity = 0;
    uint32_t temp = x_bits;
    while (temp > 0) {
        parity ^= (temp & 1);
        temp >>= 1;
    }
    /* Додаємо нелінійний вентиль AND між сусідніми бітами */
    uint8_t bit0 = (x_bits >> 0) & 1;
    uint8_t bit1 = (x_bits >> 1) & 1;
    uint8_t bit2 = (x_bits >> 2) & 1;
    
    return parity ^ (bit0 & bit1) ^ (bit1 & bit2);
}

/* Ініціалізація спрощеного комбінаторного дизайну */
static bool nw_design_init(nw_design_t *dsg) {
    if (!dsg) return false;
    dsg->seed_len = NW_SEED_LEN;
    dsg->subset_len = NW_SUBSET_LEN;
    dsg->out_len = NW_OUT_LEN;

    /* Детерміноване заповнення підмножин S_i для демонстрації */
    for (size_t i = 0; i < NW_OUT_LEN; ++i) {
        for (size_t j = 0; j < NW_SUBSET_LEN; ++j) {
            dsg->design[i][j] = (uint8_t)((i * 3 + j * 2 + (i * j)) % NW_SEED_LEN);
        }
    }
    return true;
}

/* Виділення проекції z|S_i та обчислення одного біта */
static uint8_t nw_generate_bit(const nw_design_t *dsg, const uint8_t *seed, size_t idx) {
    uint32_t sub_val = 0;
    for (size_t j = 0; j < dsg->subset_len; ++j) {
        uint8_t pos = dsg->design[idx][j];
        uint8_t bit = (seed[pos / 8] >> (pos % 8)) & 1;
        sub_val |= ((uint32_t)bit << j);
    }
    return nw_hard_function(sub_val, dsg->subset_len);
}

/* Повний процес генерації m бітів */
void nw_prg_generate(const nw_design_t *dsg, const uint8_t *seed, uint8_t *out_bits) {
    for (size_t i = 0; i < dsg->out_len; ++i) {
        out_bits[i] = nw_generate_bit(dsg, seed, i);
    }
}

int main(void) {
    nw_design_t dsg;
    if (!nw_design_init(&dsg)) {
        fprintf(stderr, "Помилка ініціалізації дизайну\n");
        return EXIT_FAILURE;
    }

    /* Насіння довжиною d = 16 біт (2 байти) */
    uint8_t seed[2] = { 0xA5, 0x5C };
    uint8_t out_stream[NW_OUT_LEN];

    nw_prg_generate(&dsg, seed, out_stream);

    printf("Псевдовипадковий бітовий потік NW PRG (m = %d біт):\n", NW_OUT_LEN);
    for (size_t i = 0; i < NW_OUT_LEN; ++i) {
        printf("%d", out_stream[i]);
        if ((i + 1) % 8 == 0) printf(" ");
    }
    printf("\n");

    return EXIT_SUCCESS;
}
