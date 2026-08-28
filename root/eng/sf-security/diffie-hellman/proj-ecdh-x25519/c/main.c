#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <openssl/evp.h>
#include <openssl/kdf.h>
#include <openssl/rand.h>

#define KEY_LEN 32
#define IV_LEN 12

typedef struct {
    uint8_t client_write_key[KEY_LEN];
    uint8_t server_write_key[KEY_LEN];
    uint8_t client_write_iv[IV_LEN];
    uint8_t server_write_iv[IV_LEN];
} session_keys_t;

static void secure_cleanse(void *ptr, size_t len) {
    OPENSSL_cleanse(ptr, len);
}

/* Генерація пари ключів X25519 */
static EVP_PKEY* generate_x25519_keypair(void) {
    EVP_PKEY_CTX *pctx = EVP_PKEY_CTX_new_id(EVP_PKEY_X25519, NULL);
    if (!pctx) return NULL;

    EVP_PKEY *pkey = NULL;
    if (EVP_PKEY_keygen_init(pctx) <= 0 || EVP_PKEY_keygen(pctx, &pkey) <= 0) {
        EVP_PKEY_CTX_free(pctx);
        return NULL;
    }
    EVP_PKEY_CTX_free(pctx);
    return pkey;
}

/* Обчислення спільного секрету K через X25519 */
static int derive_shared_secret(EVP_PKEY *our_priv, EVP_PKEY *peer_pub,
                                uint8_t *out_secret, size_t *out_len) {
    EVP_PKEY_CTX *ctx = EVP_PKEY_CTX_new(our_priv, NULL);
    if (!ctx) return 0;

    if (EVP_PKEY_derive_init(ctx) <= 0 ||
        EVP_PKEY_derive_set_peer(ctx, peer_pub) <= 0) {
        EVP_PKEY_CTX_free(ctx);
        return 0;
    }

    if (EVP_PKEY_derive(ctx, out_secret, out_len) <= 0) {
        EVP_PKEY_CTX_free(ctx);
        return 0;
    }

    EVP_PKEY_CTX_free(ctx);
    return 1;
}

/* Виведення симетричних ключів через HKDF-SHA256 (RFC 5869) */
static int derive_session_keys(const uint8_t *shared_secret, size_t secret_len,
                               const uint8_t *salt, size_t salt_len,
                               const char *info, session_keys_t *keys) {
    EVP_KDF *kdf = EVP_KDF_fetch(NULL, "HKDF", NULL);
    if (!kdf) return 0;

    EVP_KDF_CTX *kctx = EVP_KDF_CTX_new(kdf);
    EVP_KDF_free(kdf);
    if (!kctx) return 0;

    char digest[] = "SHA256";
    OSSL_PARAM params[5];
    params[0] = OSSL_PARAM_construct_utf8_string("digest", digest, sizeof(digest));
    params[1] = OSSL_PARAM_construct_octet_string("key", (void*)shared_secret, secret_len);
    params[2] = OSSL_PARAM_construct_octet_string("salt", (void*)salt, salt_len);
    params[3] = OSSL_PARAM_construct_octet_string("info", (void*)info, strlen(info));
    params[4] = OSSL_PARAM_construct_end();

    uint8_t out_material[sizeof(session_keys_t)];
    int ret = EVP_KDF_derive(kctx, out_material, sizeof(out_material), params);
    EVP_KDF_CTX_free(kctx);

    if (ret <= 0) return 0;

    memcpy(keys->client_write_key, out_material, KEY_LEN);
    memcpy(keys->server_write_key, out_material + KEY_LEN, KEY_LEN);
    memcpy(keys->client_write_iv, out_material + 2 * KEY_LEN, IV_LEN);
    memcpy(keys->server_write_iv, out_material + 2 * KEY_LEN + IV_LEN, IV_LEN);

    secure_cleanse(out_material, sizeof(out_material));
    return 1;
}

int main(void) {
    /* 1. Клієнт генерує ефемерну пару */
    EVP_PKEY *client_key = generate_x25519_keypair();
    /* 2. Сервер генерує ефемерну пару */
    EVP_PKEY *server_key = generate_x25519_keypair();
    if (!client_key || !server_key) goto cleanup;

    /* 3. Обидві сторони обчислюють спільний секрет */
    uint8_t client_secret[KEY_LEN] = {0};
    uint8_t server_secret[KEY_LEN] = {0};
    size_t client_sec_len = KEY_LEN, server_sec_len = KEY_LEN;

    if (!derive_shared_secret(client_key, server_key, client_secret, &client_sec_len) ||
        !derive_shared_secret(server_key, client_key, server_secret, &server_sec_len)) {
        goto cleanup;
    }

    /* Перевірка ідентичності секретів за сталий час */
    if (CRYPTO_memcmp(client_secret, server_secret, KEY_LEN) != 0) {
        goto cleanup;
    }

    /* 4. Виведення сесійних ключів з використанням спільної солі */
    uint8_t salt[16];
    RAND_bytes(salt, sizeof(salt));
    const char *context_info = "tls13-session-v1";

    session_keys_t client_keys, server_keys;
    derive_session_keys(client_secret, KEY_LEN, salt, sizeof(salt), context_info, &client_keys);
    derive_session_keys(server_secret, KEY_LEN, salt, sizeof(salt), context_info, &server_keys);

cleanup:
    /* 5. Негайне затирання пам'яті (PFS) */
    secure_cleanse(client_secret, sizeof(client_secret));
    secure_cleanse(server_secret, sizeof(server_secret));
    if (client_key) EVP_PKEY_free(client_key);
    if (server_key) EVP_PKEY_free(server_key);
    return 0;
}
