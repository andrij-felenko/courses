#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define FHSS_MAX_CHANNELS 256
#define FHSS_KEY_WORDS    4

/* Стан генератора криптографічного FHSS */
typedef struct {
    uint32_t key[FHSS_KEY_WORDS];  /* 128-бітний симетричний ключ */
    uint32_t net_id;               /* 32-бітний ідентифікатор мережі */
    uint16_t num_channels;         /* Загальна кількість робочих каналів (M) */
    uint8_t  blacklist_mask[FHSS_MAX_CHANNELS / 8]; /* Бітова маска чорного списку */
} fhss_crypto_engine_t;

/* Допоміжні функції побітового обертання */
static inline uint32_t rotl32(uint32_t x, uint8_t b) {
    return (x << b) | (x >> (32 - b));
}

/* Раунд криптографічного перемішування на базі ChaCha/SipHash ядра */
static inline void crypto_quarter_round(uint32_t *a, uint32_t *b, uint32_t *c, uint32_t *d) {
    *a += *b; *d ^= *a; *d = rotl32(*d, 16);
    *c += *d; *b ^= *c; *b = rotl32(*b, 12);
    *a += *b; *d ^= *a; *d = rotl32(*d, 8);
    *c += *d; *b ^= *c; *b = rotl32(*b, 7);
}

/* Ініціалізація генератора */
void fhss_init(fhss_crypto_engine_t *engine, const uint8_t key[16], uint32_t net_id, uint16_t num_channels) {
    if (!engine || num_channels == 0 || num_channels > FHSS_MAX_CHANNELS) return;

    for (size_t i = 0; i < FHSS_KEY_WORDS; ++i) {
        engine->key[i] = (uint32_t)key[i * 4 + 0] |
                         ((uint32_t)key[i * 4 + 1] << 8) |
                         ((uint32_t)key[i * 4 + 2] << 16) |
                         ((uint32_t)key[i * 4 + 3] << 24);
    }
    engine->net_id = net_id;
    engine->num_channels = num_channels;

    for (size_t i = 0; i < sizeof(engine->blacklist_mask); ++i) {
        engine->blacklist_mask[i] = 0;
    }
}

/* Блокування/розблокування каналу в чорному списку */
void fhss_set_channel_blocked(fhss_crypto_engine_t *engine, uint16_t ch, bool blocked) {
    if (!engine || ch >= engine->num_channels) return;
    if (blocked) {
        engine->blacklist_mask[ch / 8] |= (uint8_t)(1u << (ch % 8));
    } else {
        engine->blacklist_mask[ch / 8] &= (uint8_t)~(1u << (ch % 8));
    }
}

static inline bool fhss_is_blocked(const fhss_crypto_engine_t *engine, uint16_t ch) {
    return (engine->blacklist_mask[ch / 8] & (uint8_t)(1u << (ch % 8))) != 0;
}

/* Псевдовипадкова функція PRF(Key, net_id, hop_counter, attempt) */
static uint32_t fhss_prf_evaluate(const fhss_crypto_engine_t *engine, uint64_t hop_counter, uint32_t attempt) {
    uint32_t state[4];
    state[0] = engine->key[0] ^ (uint32_t)(hop_counter & 0xFFFFFFFFu);
    state[1] = engine->key[1] ^ (uint32_t)(hop_counter >> 32);
    state[2] = engine->key[2] ^ engine->net_id;
    state[3] = engine->key[3] ^ attempt;

    /* 4 раунди нелінійного перемішування */
    for (int r = 0; r < 4; ++r) {
        crypto_quarter_round(&state[0], &state[1], &state[2], &state[3]);
    }
    return state[0] ^ state[1] ^ state[2] ^ state[3];
}

/* Редукція 32-бітного псевдовипадкового числа на діапазон [0, M-1] без зміщення */
static inline uint16_t reduce_unbiased(uint32_t raw_val, uint16_t bound) {
    uint64_t mult = (uint64_t)raw_val * (uint64_t)bound;
    return (uint16_t)(mult >> 32);
}

/* Обчислення номера робочої частоти для заданого кроку часу */
uint16_t fhss_get_channel(const fhss_crypto_engine_t *engine, uint64_t hop_counter) {
    if (!engine || engine->num_channels == 0) return 0;

    for (uint32_t attempt = 0; attempt < 8; ++attempt) {
        uint32_t rand_val = fhss_prf_evaluate(engine, hop_counter, attempt);
        uint16_t candidate = reduce_unbiased(rand_val, engine->num_channels);

        if (!fhss_is_blocked(engine, candidate)) {
            return candidate;
        }
    }
    /* Якщо всі спроби виявилися заблокованими, повертаємо детермінований резервний канал */
    return (uint16_t)(hop_counter % engine->num_channels);
}
