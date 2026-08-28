#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>

/* Структура генератора LFSR у формі Фібоначчі */
typedef struct {
    uint32_t state;
    uint32_t mask;
    uint8_t  bits;
} lfsr_fibonacci_t;

/* Структура генератора LFSR у формі Галуа */
typedef struct {
    uint32_t state;
    uint32_t mask;
    uint8_t  bits;
} lfsr_galois_t;

void lfsr_fibonacci_init(lfsr_fibonacci_t *lfsr, uint32_t poly_mask, uint8_t bits, uint32_t seed) {
    lfsr->mask = poly_mask;
    lfsr->bits = bits;
    /* Захист від заклинювання у нульовому стані */
    lfsr->state = (seed == 0) ? 1U : (seed & ((1U << bits) - 1U));
}

uint8_t lfsr_fibonacci_next(lfsr_fibonacci_t *lfsr) {
    uint8_t out_bit = (lfsr->state >> (lfsr->bits - 1)) & 1U;
    uint32_t tapped = lfsr->state & lfsr->mask;
    
    /* Обчислення парності отводів (згорнутий XOR) */
    uint8_t feedback = 0;
    while (tapped > 0) {
        feedback ^= (tapped & 1U);
        tapped >>= 1U;
    }
    
    lfsr->state = ((lfsr->state << 1U) | feedback) & ((1U << lfsr->bits) - 1U);
    return out_bit;
}

void lfsr_galois_init(lfsr_galois_t *lfsr, uint32_t poly_mask, uint8_t bits, uint32_t seed) {
    lfsr->mask = poly_mask;
    lfsr->bits = bits;
    lfsr->state = (seed == 0) ? 1U : (seed & ((1U << bits) - 1U));
}

uint8_t lfsr_galois_next(lfsr_galois_t *lfsr) {
    uint8_t out_bit = lfsr->state & 1U;
    lfsr->state >>= 1U;
    if (out_bit != 0) {
        lfsr->state ^= lfsr->mask;
    }
    return out_bit;
}

/* Генерація коду Ґолда шляхом додавання двох m-послідовностей */
void generate_gold_sequence(uint32_t poly1, uint32_t poly2, uint8_t bits, 
                            uint32_t shift2, int8_t *out_buf, size_t length) {
    lfsr_galois_t gen1, gen2;
    lfsr_galois_init(&gen1, poly1, bits, 1);
    lfsr_galois_init(&gen2, poly2, bits, 1);

    /* Прокрутка другого генератора для встановлення фазового зсуву */
    for (uint32_t i = 0; i < shift2; i++) {
        lfsr_galois_next(&gen2);
    }

    for (size_t i = 0; i < length; i++) {
        uint8_t b1 = lfsr_galois_next(&gen1);
        uint8_t b2 = lfsr_galois_next(&gen2);
        uint8_t gold_bit = b1 ^ b2;
        /* Перетворення {0, 1} у біполярний сигнал {+1, -1} */
        out_buf[i] = (gold_bit == 0) ? 1 : -1;
    }
}

/* Обчислення періодичної автокореляційної функції */
int32_t compute_autocorrelation(const int8_t *seq, size_t length, size_t shift) {
    int32_t sum = 0;
    for (size_t i = 0; i < length; i++) {
        size_t shifted_idx = (i + shift) % length;
        sum += (int32_t)seq[i] * (int32_t)seq[shifted_idx];
    }
    return sum;
}

int main(void) {
    const uint8_t bits = 5;
    const size_t N = (1U << bits) - 1U; /* N = 31 */
    int8_t *seq = (int8_t *)malloc(N * sizeof(int8_t));
    if (!seq) return 1;

    /* Поліноми Ґолда m=5: x⁵ + x² + 1 (0x12) та x⁵ + x⁴ + x³ + x² + 1 (0x1E) */
    generate_gold_sequence(0x12U, 0x1EU, bits, 3, seq, N);

    printf("Період N = %zu\n", N);
    printf("АКФ на зсуві 0: %d\n", compute_autocorrelation(seq, N, 0));
    printf("АКФ на зсуві 1: %d\n", compute_autocorrelation(seq, N, 1));
    printf("АКФ на зсуві 2: %d\n", compute_autocorrelation(seq, N, 2));

    free(seq);
    return 0;
}
