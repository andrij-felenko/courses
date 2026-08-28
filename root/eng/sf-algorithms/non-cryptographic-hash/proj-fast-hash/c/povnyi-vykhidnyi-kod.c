#include <stdint.h>
#include <stddef.h>
#include <string.h>

/* Магічні константи з високою бітовою щільністю (prime constants) */
static const uint64_t C1 = 0x87c37b91114253d5ULL;
static const uint64_t C2 = 0x4cf5ad432745937fULL;
static const uint64_t FINAL_M1 = 0xff51afd7565a1a5dULL;
static const uint64_t FINAL_M2 = 0xc4ceb9fe1a85ec53ULL;

/* Циклічний зсув бітів ліворуч */
static inline uint64_t rotl64(uint64_t x, int8_t r) {
    return (x << r) | (x >> (64 - r));
}

/* Безпечне зчитування 64-бітного слова незалежно від вирівнювання */
static inline uint64_t load64(const uint8_t *p) {
    uint64_t v;
    memcpy(&v, p, sizeof(v));
    return v;
}

/* Фіналізатор (Avalanche Mixer fmix64) */
static inline uint64_t fmix64(uint64_t k) {
    k ^= k >> 33;
    k *= FINAL_M1;
    k ^= k >> 33;
    k *= FINAL_M2;
    k ^= k >> 33;
    return k;
}

/* Головна функція обчислення 64-бітного хешу */
uint64_t fast_hash64(const void *key, size_t len, uint64_t seed) {
    const uint8_t *data = (const uint8_t *)key;
    const size_t nblocks = len / 8;
    
    uint64_t h1 = seed ^ (len * C1);

    /* 1. Основний цикл обробки 64-бітних блоків */
    for (size_t i = 0; i < nblocks; i++) {
        uint64_t k1 = load64(data + i * 8);

        k1 *= C1;
        k1 = rotl64(k1, 31);
        k1 *= C2;

        h1 ^= k1;
        h1 = rotl64(h1, 27);
        h1 = h1 * 5 + 0x52dce729;
    }

    /* 2. Обробка хвоста (залишок 0..7 байтів) */
    const uint8_t *tail = data + nblocks * 8;
    uint64_t k2 = 0;

    switch (len & 7) {
    case 7: k2 ^= (uint64_t)tail[6] << 48; /* fallthrough */
    case 6: k2 ^= (uint64_t)tail[5] << 40; /* fallthrough */
    case 5: k2 ^= (uint64_t)tail[4] << 32; /* fallthrough */
    case 4: k2 ^= (uint64_t)tail[3] << 24; /* fallthrough */
    case 3: k2 ^= (uint64_t)tail[2] << 16; /* fallthrough */
    case 2: k2 ^= (uint64_t)tail[1] << 8;  /* fallthrough */
    case 1: k2 ^= (uint64_t)tail[0];
            k2 *= C1;
            k2 = rotl64(k2, 31);
            k2 *= C2;
            h1 ^= k2;
    };

    /* 3. Фінальна дифузія */
    h1 ^= len;
    return fmix64(h1);
}
