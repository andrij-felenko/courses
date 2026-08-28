#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

#define CBF_COUNTER_MAX 15

typedef struct {
    uint8_t *storage;    /* Байти для збереження 4-бітних лічильників (2 на байт) */
    size_t capacity;     /* Загальна кількість 4-бітних комірок (m) */
    size_t byte_size;    /* Розмір виділеного буфера в байтах (ceil(m / 2)) */
    uint32_t num_hashes; /* Кількість хеш-функцій (k) */
    size_t count;        /* Кількість активних елементів */
} CountingBloomFilter;

/* 32-бітний швидкий хеш MurmurHash3 */
static uint32_t murmurhash3_32(const void *key, size_t len, uint32_t seed) {
    const uint8_t *data = (const uint8_t *)key;
    const int nblocks = (int)(len / 4);
    uint32_t h1 = seed;
    const uint32_t c1 = 0xcc9e2d51;
    const uint32_t c2 = 0x1b873593;

    for (int i = 0; i < nblocks; i++) {
        uint32_t k1;
        memcpy(&k1, data + i * 4, sizeof(uint32_t));

        k1 *= c1;
        k1 = (k1 << 15) | (k1 >> 17);
        k1 *= c2;

        h1 ^= k1;
        h1 = (h1 << 13) | (h1 >> 19);
        h1 = h1 * 5 + 0xe6546b64;
    }

    const uint8_t *tail = data + nblocks * 4;
    uint32_t k1 = 0;
    switch (len & 3) {
        case 3: k1 ^= (uint32_t)tail[2] << 16; /* fallthrough */
        case 2: k1 ^= (uint32_t)tail[1] << 8;  /* fallthrough */
        case 1: k1 ^= (uint32_t)tail[0];
                k1 *= c1;
                k1 = (k1 << 15) | (k1 >> 17);
                k1 *= c2;
                h1 ^= k1;
                break;
    }

    h1 ^= (uint32_t)len;
    h1 ^= h1 >> 16;
    h1 *= 0x85ebca6b;
    h1 ^= h1 >> 13;
    h1 *= 0xc2b2ae35;
    h1 ^= h1 >> 16;

    return h1;
}

/* Читання значення 4-бітного лічильника */
static inline uint8_t cbf_get(const CountingBloomFilter *cbf, size_t index) {
    size_t byte_idx = index >> 1;
    if ((index & 1) == 0) {
        return cbf->storage[byte_idx] & 0x0F;
    } else {
        return (cbf->storage[byte_idx] >> 4) & 0x0F;
    }
}

/* Запис значення 4-бітного лічильника */
static inline void cbf_set(CountingBloomFilter *cbf, size_t index, uint8_t val) {
    size_t byte_idx = index >> 1;
    val &= 0x0F;
    if ((index & 1) == 0) {
        cbf->storage[byte_idx] = (cbf->storage[byte_idx] & 0xF0) | val;
    } else {
        cbf->storage[byte_idx] = (cbf->storage[byte_idx] & 0x0F) | (val << 4);
    }
}

/* Створення фільтра */
CountingBloomFilter *cbf_create(size_t capacity, uint32_t num_hashes) {
    if (capacity == 0 || num_hashes == 0) return NULL;

    CountingBloomFilter *cbf = (CountingBloomFilter *)malloc(sizeof(CountingBloomFilter));
    if (!cbf) return NULL;

    cbf->capacity = capacity;
    cbf->num_hashes = num_hashes;
    cbf->byte_size = (capacity + 1) / 2;
    cbf->count = 0;

    cbf->storage = (uint8_t *)calloc(cbf->byte_size, sizeof(uint8_t));
    if (!cbf->storage) {
        free(cbf);
        return NULL;
    }

    return cbf;
}

/* Звільнення ресурсів */
void cbf_destroy(CountingBloomFilter *cbf) {
    if (cbf) {
        free(cbf->storage);
        free(cbf);
    }
}

/* Додавання ключа (Insert з насичуваною арифметикою) */
bool cbf_insert(CountingBloomFilter *cbf, const void *key, size_t len) {
    if (!cbf || !key || len == 0) return false;

    uint32_t h1 = murmurhash3_32(key, len, 0x9747b28c);
    uint32_t h2 = murmurhash3_32(key, len, 0xee6b27eb);
    if (h2 == 0) h2 = 1;

    for (uint32_t i = 0; i < cbf->num_hashes; i++) {
        size_t idx = (h1 + (size_t)i * h2) % cbf->capacity;
        uint8_t cur = cbf_get(cbf, idx);
        if (cur < CBF_COUNTER_MAX) {
            cbf_set(cbf, idx, cur + 1);
        }
    }

    cbf->count++;
    return true;
}

/* Перевірка наявності ключа (Lookup) */
bool cbf_contains(const CountingBloomFilter *cbf, const void *key, size_t len) {
    if (!cbf || !key || len == 0) return false;

    uint32_t h1 = murmurhash3_32(key, len, 0x9747b28c);
    uint32_t h2 = murmurhash3_32(key, len, 0xee6b27eb);
    if (h2 == 0) h2 = 1;

    for (uint32_t i = 0; i < cbf->num_hashes; i++) {
        size_t idx = (h1 + (size_t)i * h2) % cbf->capacity;
        if (cbf_get(cbf, idx) == 0) {
            return false; /* Гарантовано відсутній */
        }
    }

    return true; /* Можливо присутній */
}

/* Видалення ключа (Delete з урахуванням заморожених лічильників) */
bool cbf_remove(CountingBloomFilter *cbf, const void *key, size_t len) {
    if (!cbf || !key || len == 0) return false;

    /* Перевіряємо наявність перед видаленням */
    if (!cbf_contains(cbf, key, len)) {
        return false;
    }

    uint32_t h1 = murmurhash3_32(key, len, 0x9747b28c);
    uint32_t h2 = murmurhash3_32(key, len, 0xee6b27eb);
    if (h2 == 0) h2 = 1;

    for (uint32_t i = 0; i < cbf->num_hashes; i++) {
        size_t idx = (h1 + (size_t)i * h2) % cbf->capacity;
        uint8_t cur = cbf_get(cbf, idx);
        /* Заморожені лічильники на максимумі 15 не декрементуються */
        if (cur > 0 && cur < CBF_COUNTER_MAX) {
            cbf_set(cbf, idx, cur - 1);
        }
    }

    if (cbf->count > 0) {
        cbf->count--;
    }
    return true;
}
