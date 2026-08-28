#include "mbedtls/ssl.h"
#include "mbedtls/pk.h"

/* Контекст апаратного модуля безпеки */
typedef struct {
    uint8_t chip_uid[16];
    uint8_t key_slot;
} hsm_context_t;

/* Апаратний callback: викликається mbedTLS замість внутрішнього софтового підпису */
int hardware_ecdsa_sign_cb(mbedtls_pk_context *ctx,
                           mbedtls_md_type_t md_alg,
                           const unsigned char *hash, size_t hash_len,
                           unsigned char *sig, size_t *sig_len,
                           int (*f_rng)(void *, unsigned char *, size_t),
                           void *p_rng) {
    (void)md_alg; (void)f_rng; (void)p_rng;
    hsm_context_t *hsm = (hsm_context_t *)ctx->pk_ctx;

    /* Виклик фізичного I2C драйвера Secure Element (наприклад, ATECC608 Sign) */
    /* Приватний ключ не читається в пам'ять: чип обчислює ECDSA над наданим hash */
    return secure_element_sign(hsm->key_slot, hash, hash_len, sig, sig_len);
}

void configure_opaque_device_key(mbedtls_pk_context *pk, hsm_context_t *hsm) {
    pk->pk_info = mbedtls_pk_info_from_type(MBEDTLS_PK_OPAQUE);
    pk->pk_ctx  = hsm;
}
