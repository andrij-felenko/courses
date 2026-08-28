#include <stdint.h>
#include <string.h>
#include <openssl/aes.h>

#define SRTP_LABEL_ENCRYPT 0x00
#define SRTP_LABEL_AUTH    0x01
#define SRTP_LABEL_SALT    0x02

typedef struct {
    uint8_t enc_key[16];   /* k_e */
    uint8_t auth_key[20];  /* k_a */
    uint8_t salt_key[14];  /* k_s */
} srtp_session_keys_t;

/* Генерація псевдовипадкового потоку за міткою Label */
static void srtp_kdf_derive(const AES_KEY *aes_ctx, const uint8_t *master_salt,
                            uint8_t label, uint8_t *out_key, size_t out_len) {
    uint8_t iv[16];
    memcpy(iv, master_salt, 14);
    iv[14] = 0;
    iv[15] = 0;

    /* Вбудовування 1-байтової мітки Label у 7-й байт солі (RFC 3711) */
    iv[7] ^= label;

    uint8_t keystream[32];
    size_t generated = 0;
    uint16_t block_counter = 0;

    while (generated < out_len) {
        iv[14] = (uint8_t)(block_counter >> 8);
        iv[15] = (uint8_t)(block_counter & 0xFF);

        AES_encrypt(iv, &keystream[generated], aes_ctx);
        generated += 16;
        block_counter++;
    }

    memcpy(out_key, keystream, out_len);
}

int srtp_derive_session_keys(const uint8_t *master_key, const uint8_t *master_salt,
                             srtp_session_keys_t *keys) {
    AES_KEY aes_ctx;
    if (AES_set_encrypt_key(master_key, 128, &aes_ctx) != 0) {
        return -1;
    }

    /* Генерація трьох незалежних сесійних ключів */
    srtp_kdf_derive(&aes_ctx, master_salt, SRTP_LABEL_ENCRYPT, keys->enc_key, 16);
    srtp_kdf_derive(&aes_ctx, master_salt, SRTP_LABEL_AUTH, keys->auth_key, 20);
    srtp_kdf_derive(&aes_ctx, master_salt, SRTP_LABEL_SALT, keys->salt_key, 14);

    return 0;
}
