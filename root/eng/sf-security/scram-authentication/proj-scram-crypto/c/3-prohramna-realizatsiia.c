#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <openssl/evp.h>
#include <openssl/hmac.h>
#include <openssl/sha.h>
#include <openssl/crypto.h>

#define SCRAM_SHA256_HASH_SIZE 32

/* Побітовий XOR двох 32-байтових криптографічних масивів */
static void scram_xor_32(uint8_t *out, const uint8_t *a, const uint8_t *b) {
    for (size_t k = 0; k < SCRAM_SHA256_HASH_SIZE; ++k) {
        out[k] = a[k] ^ b[k];
    }
}

/* Обчислення HMAC-SHA-256 над довільним повідомленням */
static int scram_hmac_sha256(const uint8_t *key, size_t key_len,
                             const uint8_t *data, size_t data_len,
                             uint8_t *out) {
    unsigned int out_len = SCRAM_SHA256_HASH_SIZE;
    uint8_t *res = HMAC(EVP_sha256(), key, (int)key_len, data, data_len, out, &out_len);
    if (!res || out_len != SCRAM_SHA256_HASH_SIZE) {
        return -1;
    }
    return 0;
}

/* Обчислення хешу SHA-256 */
static int scram_hash_sha256(const uint8_t *data, size_t data_len, uint8_t *out) {
    EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    if (!ctx) return -1;

    int ok = EVP_DigestInit_ex(ctx, EVP_sha256(), NULL) &&
             EVP_DigestUpdate(ctx, data, data_len) &&
             EVP_DigestFinal_ex(ctx, out, NULL);

    EVP_MD_CTX_free(ctx);
    return ok ? 0 : -1;
}

/* 1. Розтягування пароля за допомогою PBKDF2 */
int scram_compute_salted_password(const char *password, size_t password_len,
                                  const uint8_t *salt, size_t salt_len,
                                  int iterations,
                                  uint8_t *out_salted_password) {
    if (!PKCS5_PBKDF2_HMAC(password, (int)password_len,
                           salt, (int)salt_len,
                           iterations,
                           EVP_sha256(),
                           SCRAM_SHA256_HASH_SIZE,
                           out_salted_password)) {
        return -1;
    }
    return 0;
}

/* 2. Виведення проміжних ключів ClientKey, StoredKey та ServerKey */
int scram_derive_key_triad(const uint8_t *salted_password,
                           uint8_t *out_client_key,
                           uint8_t *out_stored_key,
                           uint8_t *out_server_key) {
    const char *label_client = "Client Key";
    const char *label_server = "Server Key";

    /* ClientKey = HMAC(SaltedPassword, "Client Key") */
    if (scram_hmac_sha256(salted_password, SCRAM_SHA256_HASH_SIZE,
                          (const uint8_t*)label_client, strlen(label_client),
                          out_client_key) != 0) {
        return -1;
    }

    /* StoredKey = SHA-256(ClientKey) */
    if (scram_hash_sha256(out_client_key, SCRAM_SHA256_HASH_SIZE, out_stored_key) != 0) {
        return -1;
    }

    /* ServerKey = HMAC(SaltedPassword, "Server Key") */
    if (scram_hmac_sha256(salted_password, SCRAM_SHA256_HASH_SIZE,
                          (const uint8_t*)label_server, strlen(label_server),
                          out_server_key) != 0) {
        return -1;
    }

    return 0;
}

/* 3. Генерація клієнтського доказу ClientProof */
int scram_create_client_proof(const uint8_t *client_key,
                              const uint8_t *stored_key,
                              const char *auth_message, size_t auth_message_len,
                              uint8_t *out_client_proof) {
    uint8_t client_signature[SCRAM_SHA256_HASH_SIZE];

    /* ClientSignature = HMAC(StoredKey, AuthMessage) */
    if (scram_hmac_sha256(stored_key, SCRAM_SHA256_HASH_SIZE,
                          (const uint8_t*)auth_message, auth_message_len,
                          client_signature) != 0) {
        return -1;
    }

    /* ClientProof = ClientKey XOR ClientSignature */
    scram_xor_32(out_client_proof, client_key, client_signature);

    /* Затирання проміжного підпису в пам'яті */
    OPENSSL_cleanse(client_signature, sizeof(client_signature));
    return 0;
}

/* 4. Серверна верифікація ClientProof та генерація ServerSignature */
int scram_verify_proof_and_generate_server_signature(
    const uint8_t *stored_key,
    const uint8_t *server_key,
    const uint8_t *client_proof,
    const char *auth_message, size_t auth_message_len,
    uint8_t *out_server_signature) {

    uint8_t client_signature[SCRAM_SHA256_HASH_SIZE];
    uint8_t recovered_client_key[SCRAM_SHA256_HASH_SIZE];
    uint8_t computed_stored_key[SCRAM_SHA256_HASH_SIZE];

    /* Крок 1: Обчислення ClientSignature = HMAC(StoredKey, AuthMessage) */
    if (scram_hmac_sha256(stored_key, SCRAM_SHA256_HASH_SIZE,
                          (const uint8_t*)auth_message, auth_message_len,
                          client_signature) != 0) {
        return -1;
    }

    /* Крок 2: Відновлення ClientKey' = ClientProof XOR ClientSignature */
    scram_xor_32(recovered_client_key, client_proof, client_signature);

    /* Крок 3: Розрахунок StoredKey' = SHA-256(ClientKey') */
    if (scram_hash_sha256(recovered_client_key, SCRAM_SHA256_HASH_SIZE,
                          computed_stored_key) != 0) {
        OPENSSL_cleanse(recovered_client_key, sizeof(recovered_client_key));
        return -1;
    }

    /* Крок 4: Порівняння StoredKey' та StoredKey у строго постійному часі */
    int match = (CRYPTO_memcmp(computed_stored_key, stored_key, SCRAM_SHA256_HASH_SIZE) == 0);

    /* Очищення секретних буферів */
    OPENSSL_cleanse(recovered_client_key, sizeof(recovered_client_key));
    OPENSSL_cleanse(computed_stored_key, sizeof(computed_stored_key));
    OPENSSL_cleanse(client_signature, sizeof(client_signature));

    if (!match) {
        return 1; /* Відхилено: недійсний пароль або порушено цілісність */
    }

    /* Крок 5: Генерація підтвердження сервера ServerSignature = HMAC(ServerKey, AuthMessage) */
    if (scram_hmac_sha256(server_key, SCRAM_SHA256_HASH_SIZE,
                          (const uint8_t*)auth_message, auth_message_len,
                          out_server_signature) != 0) {
        return -1;
    }

    return 0; /* Успішна автентифікація */
}

/* 5. Клієнтська перевірка отриманого підпису сервера */
int scram_client_verify_server_signature(const uint8_t *server_key,
                                         const char *auth_message, size_t auth_message_len,
                                         const uint8_t *received_server_signature) {
    uint8_t expected_signature[SCRAM_SHA256_HASH_SIZE];

    if (scram_hmac_sha256(server_key, SCRAM_SHA256_HASH_SIZE,
                          (const uint8_t*)auth_message, auth_message_len,
                          expected_signature) != 0) {
        return -1;
    }

    int match = (CRYPTO_memcmp(expected_signature, received_server_signature,
                               SCRAM_SHA256_HASH_SIZE) == 0);
    OPENSSL_cleanse(expected_signature, sizeof(expected_signature));
    return match ? 0 : 1;
}
