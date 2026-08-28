#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <stdbool.h>

#define KEY_SIZE           32
#define MAX_SKIPPED_KEYS   64
#define MAX_FORWARD_STEPS  256

typedef struct {
    uint8_t priv[KEY_SIZE];
    uint8_t pub[KEY_SIZE];
} dh_keypair_t;

typedef struct {
    uint8_t  dh_pub[KEY_SIZE];
    uint32_t pn;
    uint32_t n;
} msg_header_t;

typedef struct {
    uint8_t  dh_pub[KEY_SIZE];
    uint32_t n;
    uint8_t  mk[KEY_SIZE];
    bool     used;
} skipped_key_entry_t;

typedef struct {
    dh_keypair_t        dhs;             // власна пара ключів DH
    uint8_t             dhr[KEY_SIZE];   // відкритий ключ DH співрозмовника
    uint8_t             rk[KEY_SIZE];    // Root Key
    uint8_t             cks[KEY_SIZE];   // Chain Key для відправлення
    uint8_t             ckr[KEY_SIZE];   // Chain Key для отримання
    uint32_t            ns;              // лічильник відправлених
    uint32_t            nr;              // лічильник отриманих
    uint32_t            pn;              // розмір попереднього ланцюга
    bool                has_dhr;         // чи отримано перший ключ
    skipped_key_entry_t skipped[MAX_SKIPPED_KEYS];
} ratchet_state_t;

// Безпечне затирання пам'яті, захищене від оптимізацій компілятора
static void secure_memzero(void *v, size_t n) {
    volatile uint8_t *p = (volatile uint8_t *)v;
    while (n--) *p++ = 0;
}

// Заглушки криптографічних примітивів для демонстрації автомата станів
// У промисловому коді: libsodium (crypto_scalarmult_curve25519, crypto_auth_hmacsha256)
static void crypto_dh(uint8_t out[KEY_SIZE], const uint8_t priv[KEY_SIZE], const uint8_t pub[KEY_SIZE]) {
    for (int i = 0; i < KEY_SIZE; ++i) out[i] = (uint8_t)(priv[i] ^ pub[i]); // X25519
}

static void crypto_kdf_rk(uint8_t next_rk[KEY_SIZE], uint8_t next_ck[KEY_SIZE],
                          const uint8_t rk[KEY_SIZE], const uint8_t dh_out[KEY_SIZE]) {
    for (int i = 0; i < KEY_SIZE; ++i) {
        next_rk[i] = (uint8_t)(rk[i] ^ dh_out[i] ^ 0x01);
        next_ck[i] = (uint8_t)(rk[i] ^ dh_out[i] ^ 0x02);
    }
}

static void crypto_kdf_ck(uint8_t next_ck[KEY_SIZE], uint8_t mk[KEY_SIZE], const uint8_t ck[KEY_SIZE]) {
    for (int i = 0; i < KEY_SIZE; ++i) {
        mk[i]      = (uint8_t)(ck[i] ^ 0x11); // HMAC(ck, 0x01)
        next_ck[i] = (uint8_t)(ck[i] ^ 0x22); // HMAC(ck, 0x02)
    }
}

void ratchet_init(ratchet_state_t *s, const uint8_t sk[KEY_SIZE], const uint8_t peer_pub[KEY_SIZE], bool is_alice) {
    memset(s, 0, sizeof(*s));
    memcpy(s->rk, sk, KEY_SIZE);

    // Ініціалізація локальної пари ключів DH
    for (int i = 0; i < KEY_SIZE; ++i) {
        s->dhs.priv[i] = (uint8_t)(i + (is_alice ? 1 : 2));
        s->dhs.pub[i]  = (uint8_t)(s->dhs.priv[i] ^ 0xAA);
    }

    if (is_alice && peer_pub != NULL) {
        memcpy(s->dhr, peer_pub, KEY_SIZE);
        s->has_dhr = true;

        uint8_t dh_secret[KEY_SIZE];
        crypto_dh(dh_secret, s->dhs.priv, s->dhr);
        crypto_kdf_rk(s->rk, s->cks, s->rk, dh_secret);
        secure_memzero(dh_secret, sizeof(dh_secret));
    }
}

// Збереження пропущеного ключа
static int save_skipped_key(ratchet_state_t *s, const uint8_t dhr[KEY_SIZE], uint32_t n, const uint8_t mk[KEY_SIZE]) {
    for (int i = 0; i < MAX_SKIPPED_KEYS; ++i) {
        if (!s->skipped[i].used) {
            memcpy(s->skipped[i].dh_pub, dhr, KEY_SIZE);
            s->skipped[i].n = n;
            memcpy(s->skipped[i].mk, mk, KEY_SIZE);
            s->skipped[i].used = true;
            return 0;
        }
    }
    return -1; // буфер переповнено
}

// Перемотування ланцюга вперед для збереження ключів
static int skip_message_keys(ratchet_state_t *s, uint32_t until) {
    if (s->nr + MAX_FORWARD_STEPS < until) return -1;

    while (s->nr < until) {
        uint8_t mk[KEY_SIZE];
        crypto_kdf_ck(s->ckr, mk, s->ckr);
        if (save_skipped_key(s, s->dhr, s->nr, mk) != 0) {
            secure_memzero(mk, sizeof(mk));
            return -1;
        }
        secure_memzero(mk, sizeof(mk));
        s->nr++;
    }
    return 0;
}

// Крок шифрування
int ratchet_encrypt_step(ratchet_state_t *s, msg_header_t *hdr, uint8_t mk_out[KEY_SIZE]) {
    crypto_kdf_ck(s->cks, mk_out, s->cks);

    memcpy(hdr->dh_pub, s->dhs.pub, KEY_SIZE);
    hdr->pn = s->pn;
    hdr->n  = s->ns++;
    return 0;
}

// Крок дешифрування
int ratchet_decrypt_step(ratchet_state_t *s, const msg_header_t *hdr, uint8_t mk_out[KEY_SIZE]) {
    // 1. Перевірка таблиці збережених ключів
    for (int i = 0; i < MAX_SKIPPED_KEYS; ++i) {
        if (s->skipped[i].used && s->skipped[i].n == hdr->n &&
            memcmp(s->skipped[i].dh_pub, hdr->dh_pub, KEY_SIZE) == 0) {
            memcpy(mk_out, s->skipped[i].mk, KEY_SIZE);
            secure_memzero(s->skipped[i].mk, KEY_SIZE);
            s->skipped[i].used = false;
            return 0;
        }
    }

    // 2. Якщо отримано новий відкритий ключ DH — виконуємо асиметричний храповик
    if (!s->has_dhr || memcmp(hdr->dh_pub, s->dhr, KEY_SIZE) != 0) {
        if (s->has_dhr) {
            if (skip_message_keys(s, hdr->pn) != 0) return -1;
        }

        // Крок DH з новим ключем отримувача
        memcpy(s->dhr, hdr->dh_pub, KEY_SIZE);
        s->has_dhr = true;

        uint8_t dh_secret[KEY_SIZE];
        crypto_dh(dh_secret, s->dhs.priv, s->dhr);
        crypto_kdf_rk(s->rk, s->ckr, s->rk, dh_secret);

        // Генерація нової пари DH для наших наступних відповідей
        for (int i = 0; i < KEY_SIZE; ++i) s->dhs.priv[i] = (uint8_t)(s->dhs.priv[i] + 1);
        for (int i = 0; i < KEY_SIZE; ++i) s->dhs.pub[i] = (uint8_t)(s->dhs.priv[i] ^ 0xAA);

        crypto_dh(dh_secret, s->dhs.priv, s->dhr);
        crypto_kdf_rk(s->rk, s->cks, s->rk, dh_secret);
        secure_memzero(dh_secret, sizeof(dh_secret));

        s->pn = s->ns;
        s->ns = 0;
        s->nr = 0;
    }

    // 3. Перемотування поточного ланцюга отримання
    if (skip_message_keys(s, hdr->n) != 0) return -1;

    // 4. Отримання шуканого ключа повідомлення
    crypto_kdf_ck(s->ckr, mk_out, s->ckr);
    s->nr++;
    return 0;
}
