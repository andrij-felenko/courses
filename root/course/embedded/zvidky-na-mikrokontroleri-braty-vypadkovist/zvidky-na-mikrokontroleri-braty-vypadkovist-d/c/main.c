/* ============================================================================
 * Вбудована криптографічна система випадковості (C99 / MCU Embedded)
 * Джерела: Timer Capture Jitter + ADC LSB + Von Neumann + ChaCha20-DRBG
 * ============================================================================ */

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define CHACHA20_KEY_SIZE   32
#define CHACHA20_NONCE_SIZE 12
#define CHACHA20_BLOCK_SIZE 64
#define ENTROPY_POOL_SIZE   64

/* ── 1. Онлайн-тест працездатності ентропії (NIST SP 800-90B RCT) ─────────── */
typedef struct {
    uint8_t  last_sample;
    uint32_t repeat_count;
    uint32_t rct_cutoff;        /* Поріг відсікання однакових значень */
    uint32_t total_samples;
    uint32_t ones_count;        /* Лічильник монобітів */
    bool     health_fault;
} EntropyHealthMonitor;

static void health_monitor_init(EntropyHealthMonitor *hm, uint32_t cutoff) {
    hm->last_sample = 0xFF;
    hm->repeat_count = 0;
    hm->rct_cutoff = cutoff;    /* Зазвичай 16-32 для 8-бітних шумів */
    hm->total_samples = 0;
    hm->ones_count = 0;
    hm->health_fault = false;
}

static bool health_monitor_update(EntropyHealthMonitor *hm, uint8_t sample) {
    if (hm->health_fault) return false;

    /* Repetition Count Test (RCT) */
    if (sample == hm->last_sample) {
        hm->repeat_count++;
        if (hm->repeat_count >= hm->rct_cutoff) {
            hm->health_fault = true; /* Аварія: джерело шуму залипло! */
            return false;
        }
    } else {
        hm->last_sample = sample;
        hm->repeat_count = 1;
    }

    /* Моніторинг балансу бітів */
    for (int i = 0; i < 8; i++) {
        if ((sample >> i) & 1) hm->ones_count++;
    }
    hm->total_samples++;

    return true;
}

/* ── 2. Декорелятор Джона фон Неймана ─────────────────────────────────────── */
typedef struct {
    uint8_t bit_buffer;
    uint8_t bit_count;
    uint8_t out_byte;
    uint8_t out_bits_collected;
} VonNeumannExtractor;

static void vn_extractor_init(VonNeumannExtractor *vn) {
    vn->bit_buffer = 0;
    vn->bit_count = 0;
    vn->out_byte = 0;
    vn->out_bits_collected = 0;
}

/* Подає один сирий біт. Повертає true, якщо сформовано повноцінний вихідний байт */
static bool vn_extractor_feed_bit(VonNeumannExtractor *vn, uint8_t in_bit, uint8_t *out_byte) {
    in_bit &= 1;
    vn->bit_buffer = (vn->bit_buffer << 1) | in_bit;
    vn->bit_count++;

    if (vn->bit_count >= 2) {
        uint8_t pair = vn->bit_buffer & 0x03;
        vn->bit_count = 0;

        if (pair == 1) {        /* Пара 01 -> видати біт 0 */
            vn->out_byte = (vn->out_byte << 1);
            vn->out_bits_collected++;
        } else if (pair == 2) { /* Пара 10 -> видати біт 1 */
            vn->out_byte = (vn->out_byte << 1) | 1;
            vn->out_bits_collected++;
        }
        /* Пари 00 та 11 відкидаються */

        if (vn->out_bits_collected >= 8) {
            *out_byte = vn->out_byte;
            vn->out_byte = 0;
            vn->out_bits_collected = 0;
            return true;
        }
    }
    return false;
}

/* ── 3. Криптографічний генератор ChaCha20-DRBG ────────────────────────────── */
#define ROTL32(v, n) (((v) << (n)) | ((v) >> (32 - (n))))
#define CHACHA_QUARTERROUND(a, b, c, d) \
    a += b; d ^= a; d = ROTL32(d, 16); \
    c += d; b ^= c; b = ROTL32(b, 12); \
    a += b; d ^= a; d = ROTL32(d,  8); \
    c += d; b ^= c; b = ROTL32(b,  7);

typedef struct {
    uint32_t state[16];
    uint8_t  keystream[64];
    size_t   keystream_idx;
    uint32_t reseed_counter;
} ChaCha20_CSPRNG;

static void chacha20_block(const uint32_t in_state[16], uint8_t out[64]) {
    uint32_t x[16];
    memcpy(x, in_state, sizeof(x));

    /* 20 раундів ChaCha (10 подвійних раундів) */
    for (int i = 0; i < 10; i++) {
        /* Стовпчики */
        CHACHA_QUARTERROUND(x[0], x[4], x[ 8], x[12]);
        CHACHA_QUARTERROUND(x[1], x[5], x[ 9], x[13]);
        CHACHA_QUARTERROUND(x[2], x[6], x[10], x[14]);
        CHACHA_QUARTERROUND(x[3], x[7], x[11], x[15]);
        /* Діагоналі */
        CHACHA_QUARTERROUND(x[0], x[5], x[10], x[15]);
        CHACHA_QUARTERROUND(x[1], x[6], x[11], x[12]);
        CHACHA_QUARTERROUND(x[2], x[7], x[ 8], x[13]);
        CHACHA_QUARTERROUND(x[3], x[4], x[ 9], x[14]);
    }

    for (int i = 0; i < 16; i++) {
        uint32_t val = x[i] + in_state[i];
        out[i * 4 + 0] = (uint8_t)(val);
        out[i * 4 + 1] = (uint8_t)(val >> 8);
        out[i * 4 + 2] = (uint8_t)(val >> 16);
        out[i * 4 + 3] = (uint8_t)(val >> 24);
    }
}

static void csprng_seed(ChaCha20_CSPRNG *rng, const uint8_t seed[32]) {
    /* Константи ChaCha20 ("expand 32-byte k") */
    rng->state[0] = 0x61707865;
    rng->state[1] = 0x3320646e;
    rng->state[2] = 0x79622d32;
    rng->state[3] = 0x6b206574;

    /* 256-бітний ключ ентропії */
    for (int i = 0; i < 8; i++) {
        rng->state[4 + i] = (uint32_t)seed[i * 4 + 0]       |
                           ((uint32_t)seed[i * 4 + 1] <<  8) |
                           ((uint32_t)seed[i * 4 + 2] << 16) |
                           ((uint32_t)seed[i * 4 + 3] << 24);
    }

    /* Лічильник блоку та 96-бітний nonce */
    rng->state[12] = 0;
    rng->state[13] = 0x55AA55AA;
    rng->state[14] = 0x12345678;
    rng->state[15] = 0x9ABCDEF0;

    rng->keystream_idx = 64; /* Примусовий виклик першої генерації */
    rng->reseed_counter = 1;
}

/* Генерація випадкових байтів із захистом від компрометації минулого */
static void csprng_generate(ChaCha20_CSPRNG *rng, uint8_t *out, size_t len) {
    while (len > 0) {
        if (rng->keystream_idx >= 64) {
            chacha20_block(rng->state, rng->keystream);
            rng->state[12]++; /* Інкремент 32-бітного лічильника блоків */
            if (rng->state[12] == 0) rng->state[13]++;
            rng->keystream_idx = 0;
        }

        size_t available = 64 - rng->keystream_idx;
        size_t to_copy = (len < available) ? len : available;

        memcpy(out, &rng->keystream[rng->keystream_idx], to_copy);
        out += to_copy;
        len -= to_copy;
        rng->keystream_idx += to_copy;
    }

    /* Backtracking Resistance: негайне оновлення ключа наступним блоком */
    uint8_t next_key_block[64];
    chacha20_block(rng->state, next_key_block);
    rng->state[12]++;

    for (int i = 0; i < 8; i++) {
        rng->state[4 + i] = (uint32_t)next_key_block[i * 4 + 0]       |
                           ((uint32_t)next_key_block[i * 4 + 1] <<  8) |
                           ((uint32_t)next_key_block[i * 4 + 2] << 16) |
                           ((uint32_t)next_key_block[i * 4 + 3] << 24);
    }
    memset(next_key_block, 0, sizeof(next_key_block)); /* Очищення стеку */
    rng->keystream_idx = 64;                           /* Скидання залишкової гами */
}
