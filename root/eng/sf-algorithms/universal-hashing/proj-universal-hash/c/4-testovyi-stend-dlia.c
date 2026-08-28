#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <stdint.h>

/* Фіксована слабка хеш-функція (FNV-1a 32-bit mod m) */
uint32_t fnv1a_fixed(uint32_t key, uint32_t m) {
    uint32_t hash = 2166136261U;
    hash = (hash ^ (key & 0xFF)) * 16777619U;
    hash = (hash ^ ((key >> 8) & 0xFF)) * 16777619U;
    return hash % m;
}

int main(void) {
    const uint32_t m = 1024;
    const uint32_t n = 10000;
    
    /* Збір підрахованого набору ключів для колізій під FNV-1a */
    uint32_t *bad_keys = malloc(n * sizeof(uint32_t));
    uint32_t count = 0;
    uint32_t candidate = 0;
    
    while (count < n) {
        if (fnv1a_fixed(candidate, m) == 42) {
            bad_keys[count++] = candidate;
        }
        candidate++;
    }
    
    printf("Сформовано %u колізійних ключів для бакета [42]\n", n);
    
    /* Оцінка універсального хешера на тих самих "поганих" ключах */
    multiply_shift_hasher_t univ_h;
    multiply_shift_init(&univ_h, 10, 0x9E3779B97F4A7C15ULL);
    
    uint32_t max_chain = 0;
    uint32_t buckets[1024] = {0};
    
    for (uint32_t i = 0; i < n; i++) {
        uint64_t h_val = multiply_shift_eval(&univ_h, bad_keys[i]);
        buckets[h_val]++;
    }
    
    for (uint32_t i = 0; i < m; i++) {
        if (buckets[i] > max_chain) max_chain = buckets[i];
    }
    
    printf("Максимальна довжина ланцюжка універсального хешування: %u\n", max_chain);
    
    free(bad_keys);
    return 0;
}
