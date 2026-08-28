#include <stdio.h>
#include <stdlib.h>

#define BLOOM_SIZE 16

typedef struct {
    unsigned char bits[BLOOM_SIZE / 8];
} BloomFilter;

void bloom_add(BloomFilter* bf, int val) {
    int h1 = (val * 7 + 3) % BLOOM_SIZE;
    int h2 = (val * 13 + 5) % BLOOM_SIZE;
    bf->bits[h1 / 8] |= (1 << (h1 % 8));
    bf->bits[h2 / 8] |= (1 << (h2 % 8));
}

int bloom_check(const BloomFilter* bf, int val) {
    int h1 = (val * 7 + 3) % BLOOM_SIZE;
    int h2 = (val * 13 + 5) % BLOOM_SIZE;
    int bit1 = (bf->bits[h1 / 8] >> (h1 % 8)) & 1;
    int bit2 = (bf->bits[h2 / 8] >> (h2 % 8)) & 1;
    return bit1 && bit2;
}

int main(void) {
    BloomFilter bf = {{0}};
    printf("=== Фільтр Блума: M = %d бітів ===\n", BLOOM_SIZE);
    int elements[] = { 1, 4, 9, 12, 15 };

    for (size_t i = 0; i < 5; ++i) {
        bloom_add(&bf, elements[i]);
    }

    // Перевірка елемента, якого НЕ додавали (тест колізії Діріхле)
    int test_val = 7;
    if (bloom_check(&bf, test_val)) {
        printf("Елемент %d не додавався, але фільтр каже 'присутній' (колізія Блума/Діріхле!)\n", test_val);
    } else {
        printf("Елемент %d відсутній.\n", test_val);
    }

    return 0;
}
