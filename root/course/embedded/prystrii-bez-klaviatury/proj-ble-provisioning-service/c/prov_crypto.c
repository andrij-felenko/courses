#include "prov_crypto.h"
#include "prov_platform.h"

#include <string.h>

/*
 * Точки малого порядку Curve25519 (порядок 1, 2, 4 і 8) плюс канонічні
 * представлення p-1, p, p+1. Спільний секрет із такою точкою вироджується,
 * і атакуючий наперед знає ключ сесії.
 */
static const uint8_t k_small_order[7][PROV_KEY_SIZE] = {
    /* 0 — порядок 4 */
    { 0x00 },
    /* 1 — порядок 1 */
    { 0x01 },
    /* порядок 8 */
    { 0xe0, 0xeb, 0x7a, 0x7c, 0x3b, 0x41, 0xb8, 0xae, 0x16, 0x56, 0xe3,
      0xfa, 0xf1, 0x9f, 0xc4, 0x6a, 0xda, 0x09, 0x8d, 0xeb, 0x9c, 0x32,
      0xb1, 0xfd, 0x86, 0x62, 0x05, 0x16, 0x5f, 0x49, 0xb8, 0x00 },
    /* порядок 8 */
    { 0x5f, 0x9c, 0x95, 0xbc, 0xa3, 0x50, 0x8c, 0x24, 0xb1, 0xd0, 0xb1,
      0x55, 0x9c, 0x83, 0xef, 0x5b, 0x04, 0x44, 0x5c, 0xc4, 0x58, 0x1c,
      0x8e, 0x86, 0xd8, 0x22, 0x4e, 0xdd, 0xd0, 0x9f, 0x11, 0x57 },
    /* p-1 — порядок 2 */
    { 0xec, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
      0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
      0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x7f },
    /* p — порядок 4 */
    { 0xed, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
      0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
      0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x7f },
    /* p+1 — порядок 1 */
    { 0xee, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
      0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
      0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0x7f }
};

void prov_secure_wipe(void *ptr, size_t len)
{
    volatile uint8_t *p = (volatile uint8_t *)ptr;
    while (len--) {
        *p++ = 0;
    }
}

bool prov_ct_equal(const uint8_t *a, const uint8_t *b, size_t len)
{
    uint8_t diff = 0;
    for (size_t i = 0; i < len; ++i) {
        diff |= (uint8_t)(a[i] ^ b[i]);
    }
    return diff == 0;
}

/* 1, якщо x == 0, і 0 інакше — без розгалуження. */
static uint8_t byte_is_zero(uint8_t x)
{
    return (uint8_t)(((uint32_t)x - 1u) >> 31);
}

static bool is_small_order(const uint8_t pub[PROV_KEY_SIZE])
{
    uint8_t hit = 0;
    for (size_t i = 0; i < sizeof(k_small_order) / PROV_KEY_SIZE; ++i) {
        uint8_t diff = 0;
        for (size_t b = 0; b < PROV_KEY_SIZE - 1; ++b) {
            diff |= (uint8_t)(pub[b] ^ k_small_order[i][b]);
        }
        /* Старший біт u-координати ігнорується (RFC 7748 §5): без цього
           та сама точка з піднятим бітом пройшла б повз таблицю. */
        diff |= (uint8_t)((pub[PROV_KEY_SIZE - 1] & 0x7F) ^ k_small_order[i][PROV_KEY_SIZE - 1]);
        hit |= byte_is_zero(diff);
    }
    return hit != 0;
}

bool prov_pubkey_acceptable(const uint8_t pub[PROV_KEY_SIZE])
{
    uint8_t any_bit = 0x00;
    uint8_t all_bits = 0xFF;
    for (size_t i = 0; i < PROV_KEY_SIZE; ++i) {
        any_bit |= pub[i];
        all_bits &= pub[i];
    }
    if (any_bit == 0x00) {
        return false;               /* суцільні нулі */
    }
    if (all_bits == 0xFF) {
        return false;               /* суцільні одиниці: до того ж не канонічне число */
    }
    return !is_small_order(pub);
}

void prov_clamp_scalar(uint8_t priv[PROV_KEY_SIZE])
{
    priv[0] &= 248;                 /* три молодші біти геть — кофактор h = 8 */
    priv[PROV_KEY_SIZE - 1] &= 127; /* старший біт u-координати не наш */
    priv[PROV_KEY_SIZE - 1] |= 64;  /* фіксуємо порядок скаляра */
}

void prov_keypair(uint8_t priv[PROV_KEY_SIZE], uint8_t pub[PROV_KEY_SIZE])
{
    plat_random_bytes(priv, PROV_KEY_SIZE);
    prov_clamp_scalar(priv);
    plat_x25519_public(priv, pub);
}

bool prov_pop_proof_valid(const uint8_t *pop, size_t pop_len,
                          const uint8_t client_pub[PROV_KEY_SIZE],
                          const uint8_t proof[PROV_PROOF_SIZE])
{
    uint8_t expected[PROV_PROOF_SIZE];
    plat_hmac_sha256(pop, pop_len, client_pub, PROV_KEY_SIZE, expected);
    bool ok = prov_ct_equal(expected, proof, PROV_PROOF_SIZE);
    prov_secure_wipe(expected, sizeof(expected));
    return ok;
}

bool prov_derive_session_key(const uint8_t our_priv[PROV_KEY_SIZE],
                             const uint8_t client_pub[PROV_KEY_SIZE],
                             const uint8_t device_pub[PROV_KEY_SIZE],
                             const uint8_t salt[PROV_SALT_SIZE],
                             const uint8_t *pop, size_t pop_len,
                             uint8_t out_key[PROV_KEY_SIZE])
{
    static const char k_label[] = "prov-v1-aes256gcm";
    const size_t label_len = sizeof(k_label) - 1;

    if (pop_len > PROV_POP_MAX_LEN) {
        return false;
    }

    uint8_t shared[PROV_KEY_SIZE];
    if (!plat_x25519(our_priv, client_pub, shared)) {
        prov_secure_wipe(shared, sizeof(shared));
        return false;
    }

    /* RFC 7748 §6.1: нульовий спільний секрет означає, що точка малого
       порядку все ж прослизнула. Друга лінія оборони після таблиці. */
    uint8_t any_bit = 0;
    for (size_t i = 0; i < PROV_KEY_SIZE; ++i) {
        any_bit |= shared[i];
    }
    if (any_bit == 0) {
        prov_secure_wipe(shared, sizeof(shared));
        return false;
    }

    /* info звʼязує ключ із PoP і з обома публічними ключами: підміна
       будь-якого з них дає інший ключ, і тег GMAC перестане сходитися. */
    uint8_t info[sizeof(k_label) - 1 + PROV_POP_MAX_LEN + 2 * PROV_KEY_SIZE];
    size_t n = 0;
    memcpy(info + n, k_label, label_len);          n += label_len;
    memcpy(info + n, pop, pop_len);                n += pop_len;
    memcpy(info + n, client_pub, PROV_KEY_SIZE);   n += PROV_KEY_SIZE;
    memcpy(info + n, device_pub, PROV_KEY_SIZE);   n += PROV_KEY_SIZE;

    plat_hkdf_sha256(salt, PROV_SALT_SIZE,
                     shared, PROV_KEY_SIZE,
                     info, n,
                     out_key, PROV_KEY_SIZE);

    prov_secure_wipe(shared, sizeof(shared));
    prov_secure_wipe(info, sizeof(info));
    return true;
}
