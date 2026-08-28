#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <stdbool.h>

#define KEY_LEN       32
#define TAG_LEN       16

typedef struct {
    uint8_t  dh_pub[KEY_LEN];
    uint32_t pn;
    uint32_t n;
} message_header_t;

typedef struct {
    uint8_t cks[KEY_LEN];   // ключ ланцюга відправлення
    uint8_t dhs_pub[KEY_LEN];
    uint32_t ns;            // лічильник повідомлень
    uint32_t pn;            // розмір попереднього ланцюга
} sender_state_t;

// Безпечне очищення конфіденційної пам'яті
static void secure_wipe(void *ptr, size_t len) {
    volatile uint8_t *p = (volatile uint8_t *)ptr;
    while (len--) *p++ = 0;
}

// Псевдо-функція HMAC для демонстрації кроку KDF
static void kdf_step(uint8_t next_ck[KEY_LEN], uint8_t mk[KEY_LEN], const uint8_t ck[KEY_LEN]) {
    for (int i = 0; i < KEY_LEN; ++i) {
        mk[i]      = (uint8_t)(ck[i] ^ 0x01); // HMAC(ck, 0x01)
        next_ck[i] = (uint8_t)(ck[i] ^ 0x02); // HMAC(ck, 0x02)
    }
}

// Спрощена заглушка AEAD (у реальності: crypto_aead_chacha20poly1305_encrypt)
static void aead_encrypt(
    uint8_t *ciphertext, uint8_t tag[TAG_LEN],
    const uint8_t *plaintext, size_t len,
    const uint8_t *aad, size_t aad_len,
    const uint8_t key[KEY_LEN]
) {
    for (size_t i = 0; i < len; ++i) ciphertext[i] = plaintext[i] ^ key[i % KEY_LEN];
    for (size_t i = 0; i < TAG_LEN; ++i) tag[i] = (uint8_t)(key[i] ^ (aad_len > 0 ? aad[0] : 0));
}

int encrypt_message(
    sender_state_t *state,
    const uint8_t *plaintext, size_t plaintext_len,
    message_header_t *out_hdr,
    uint8_t *out_ciphertext, uint8_t out_tag[TAG_LEN]
) {
    uint8_t mk[KEY_LEN];

    // 1. Крок симетричного храповика
    kdf_step(state->cks, mk, state->cks);

    // 2. Формування заголовка (асоційовані дані для AEAD)
    memcpy(out_hdr->dh_pub, state->dhs_pub, KEY_LEN);
    out_hdr->pn = state->pn;
    out_hdr->n  = state->ns++;

    // 3. Автентифіковане шифрування з AAD
    aead_encrypt(out_ciphertext, out_tag,
                 plaintext, plaintext_len,
                 (const uint8_t *)out_hdr, sizeof(message_header_t),
                 mk);

    // 4. Негайне затирання ключа повідомлення
    secure_wipe(mk, sizeof(mk));
    return 0;
}
