#include <stdio.h>
#include <string.h>
#include <openssl/evp.h>
#include <openssl/params.h>
#include <openssl/core_names.h>

int compute_hmac_sha256(const unsigned char *key, size_t key_len,
                        const unsigned char *msg, size_t msg_len,
                        unsigned char *out_tag, size_t *out_tag_len) {
    EVP_MAC *mac = NULL;
    EVP_MAC_CTX *ctx = NULL;
    int success = 0;

    /* 1. Завантаження провайдера алгоритму HMAC */
    mac = EVP_MAC_fetch(NULL, "HMAC", NULL);
    if (!mac) goto cleanup;

    /* 2. Створення робочого контексту */
    ctx = EVP_MAC_CTX_new(mac);
    if (!ctx) goto cleanup;

    /* 3. Налаштування параметрів: вибір геш-функції SHA-256 */
    OSSL_PARAM params[2];
    params[0] = OSSL_PARAM_construct_utf8_string(OSSL_MAC_PARAM_DIGEST, "SHA256", 0);
    params[1] = OSSL_PARAM_construct_end();

    /* 4. Ініціалізація контексту ключем та параметрами */
    if (!EVP_MAC_init(ctx, key, key_len, params)) goto cleanup;

    /* 5. Потокова передача даних повідомлення */
    if (!EVP_MAC_update(ctx, msg, msg_len)) goto cleanup;

    /* 6. Фіналізація та отримання 32-байтного тегу */
    if (!EVP_MAC_final(ctx, out_tag, out_tag_len, 32)) goto cleanup;

    success = 1;

cleanup:
    if (ctx) EVP_MAC_CTX_free(ctx);
    if (mac) EVP_MAC_free(mac);
    return success;
}
