#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define SYNCOOKIE_TIME_SHIFT 6          /* Дискретність вікна: 2^6 = 64 секунди */
#define SYNCOOKIE_TIME_MASK  0x07       /* 3 біти для мітки часу (0..7) */
#define SYNCOOKIE_MSS_MASK   0x07       /* 3 біти для індексу MSS (0..7) */
#define SYNCOOKIE_HASH_MASK  0x03FFFFFF /* 26 бітів для криптографічного MAC */

/* Стандартна таблиця значень TCP MSS для 3-бітного індексу */
static const uint16_t MSS_TABLE[8] = {
    536,   /* Мінімальний IPv4 MSS */
    1200,  /* Безпечний розмір для тунелів */
    1400,  /* Стандартний GRE/IPsec */
    1440,  /* PPPoE / Cloudflare Edge */
    1452,  /* Стандартний PPPoE DSL */
    1460,  /* Типовий Ethernet IPv4 (1500 - 40) */
    8960,  /* Jumbo Frame без заголовків */
    9000   /* Максимальний Ethernet Jumbo Frame */
};

/* Раунд змішування SipHash для швидкого обчислення 26-бітного MAC */
static uint32_t siphash_syn(uint32_t saddr, uint32_t daddr,
                            uint16_t sport, uint16_t dport,
                            uint32_t client_isn, uint32_t time_idx,
                            const uint8_t secret[16]) {
    uint64_t k0, k1;
    memcpy(&k0, secret, 8);
    memcpy(&k1, secret + 8, 8);

    uint64_t v0 = 0x736f6d6570736575ULL ^ k0;
    uint64_t v1 = 0x646f72616e646f6dULL ^ k1;
    uint64_t v2 = 0x6c7967656e657261ULL ^ k0;
    uint64_t v3 = 0x7465646279746573ULL ^ k1;

    uint64_t m0 = ((uint64_t)saddr << 32) | daddr;
    uint64_t m1 = ((uint64_t)sport << 48) | ((uint64_t)dport << 32) | (client_isn ^ time_idx);

    /* Раунд змішування для m0 */
    v3 ^= m0;
    v0 += v1; v1 = (v1 << 13) | (v1 >> (64 - 13)); v1 ^= v0; v0 = (v0 << 32) | (v0 >> 32);
    v2 += v3; v3 = (v3 << 16) | (v3 >> (64 - 16)); v3 ^= v2;
    v0 += v3; v3 = (v3 << 21) | (v3 >> (64 - 21)); v3 ^= v0;
    v2 += v1; v1 = (v1 << 17) | (v1 >> (64 - 17)); v1 ^= v2; v2 = (v2 << 32) | (v2 >> 32);
    v0 ^= m0;

    /* Раунд змішування для m1 */
    v3 ^= m1;
    v0 += v1; v1 = (v1 << 13) | (v1 >> (64 - 13)); v1 ^= v0; v0 = (v0 << 32) | (v0 >> 32);
    v2 += v3; v3 = (v3 << 16) | (v3 >> (64 - 16)); v3 ^= v2;
    v0 += v3; v3 = (v3 << 21) | (v3 >> (64 - 21)); v3 ^= v0;
    v2 += v1; v1 = (v1 << 17) | (v1 >> (64 - 17)); v1 ^= v2; v2 = (v2 << 32) | (v2 >> 32);
    v0 ^= m1;

    v2 ^= 0xff;
    /* Фіналізація */
    v0 += v1; v1 = (v1 << 13) | (v1 >> (64 - 13)); v1 ^= v0; v0 = (v0 << 32) | (v0 >> 32);
    v2 += v3; v3 = (v3 << 16) | (v3 >> (64 - 16)); v3 ^= v2;

    return (uint32_t)((v0 ^ v1 ^ v2 ^ v3) & SYNCOOKIE_HASH_MASK);
}

/* Пошук найближчого індексу MSS, який не перевищує запитаний клієнтом */
static uint32_t select_mss_index(uint16_t client_mss) {
    uint32_t best_idx = 0;
    for (uint32_t i = 0; i < 8; ++i) {
        if (MSS_TABLE[i] <= client_mss) {
            best_idx = i;
        } else {
            break;
        }
    }
    return best_idx;
}

/* Генерація 32-бітного ISN для відповіді SYN-ACK */
uint32_t generate_syn_cookie(uint32_t saddr, uint32_t daddr,
                             uint16_t sport, uint16_t dport,
                             uint32_t client_isn, uint16_t client_mss,
                             uint32_t now_sec, const uint8_t secret[16]) {
    uint32_t time_idx = (now_sec >> SYNCOOKIE_TIME_SHIFT) & SYNCOOKIE_TIME_MASK;
    uint32_t mss_idx = select_mss_index(client_mss);
    uint32_t hash_val = siphash_syn(saddr, daddr, sport, dport, client_isn, time_idx, secret);

    return (time_idx << 29) | (mss_idx << 26) | hash_val;
}

/* Перевірка куки у вхідному пакеті ACK: ack_seq = cookie + 1 */
bool verify_syn_cookie(uint32_t cookie, uint32_t saddr, uint32_t daddr,
                       uint16_t sport, uint16_t dport,
                       uint32_t client_isn, uint32_t now_sec,
                       const uint8_t secret[16], uint16_t *recovered_mss) {
    uint32_t cookie_time = (cookie >> 29) & SYNCOOKIE_TIME_MASK;
    uint32_t cookie_mss_idx = (cookie >> 26) & SYNCOOKIE_MSS_MASK;
    uint32_t cookie_hash = cookie & SYNCOOKIE_HASH_MASK;

    uint32_t current_time = (now_sec >> SYNCOOKIE_TIME_SHIFT) & SYNCOOKIE_TIME_MASK;

    /* Дозволяємо поточне часове вікно або попереднє (вікно допустимості ~64-128 с) */
    uint32_t diff = (current_time - cookie_time) & SYNCOOKIE_TIME_MASK;
    if (diff > 1) {
        return false; /* Кука застаріла або з майбутнього */
    }

    uint32_t expected_hash = siphash_syn(saddr, daddr, sport, dport, client_isn, cookie_time, secret);
    if (expected_hash != cookie_hash) {
        return false; /* Невалідний криптографічний MAC */
    }

    if (recovered_mss) {
        *recovered_mss = MSS_TABLE[cookie_mss_idx];
    }
    return true;
}
