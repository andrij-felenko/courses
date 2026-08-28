#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/crypto.h>

#define KEY_SIZE_256   32
#define GCM_IV_SIZE    12
#define GCM_TAG_SIZE   16

// Структура упакованого зашифрованого конверта
typedef struct {
    uint8_t wrapped_dek[KEY_SIZE_256 + GCM_TAG_SIZE]; // Зашифрований DEK + Tag обгортки
    uint8_t iv_dek[GCM_IV_SIZE];                       // IV для обгортання DEK
    uint8_t iv_data[GCM_IV_SIZE];                      // IV для шифрування корисних даних
    uint8_t tag_data[GCM_TAG_SIZE];                    // Автентифікаційний тег даних
    uint8_t *ciphertext;                               // Тіло зашифрованих даних
    size_t ciphertext_len;                             // Довжина шифротексту
} envelope_t;

// Допоміжна функція AES-256-GCM шифрування
static bool aes_gcm_encrypt(const uint8_t *key, const uint8_t *iv,
                            const uint8_t *aad, size_t aad_len,
                            const uint8_t *plain, size_t plain_len,
                            uint8_t *cipher, uint8_t *tag) {
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx) return false;

    int len = 0;
    bool success = false;

    if (EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL) != 1) goto cleanup;
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, GCM_IV_SIZE, NULL) != 1) goto cleanup;
    if (EVP_EncryptInit_ex(ctx, NULL, NULL, key, iv) != 1) goto cleanup;

    // Передача додаткових автентифікованих даних (AAD)
    if (aad && aad_len > 0) {
        if (EVP_EncryptUpdate(ctx, NULL, &len, aad, (int)aad_len) != 1) goto cleanup;
    }

    // Шифрування відкритого тексту
    if (EVP_EncryptUpdate(ctx, cipher, &len, plain, (int)plain_len) != 1) goto cleanup;
    if (EVP_EncryptFinal_ex(ctx, cipher + len, &len) != 1) goto cleanup;

    // Отримання тегу автентифікації
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_GET_TAG, GCM_TAG_SIZE, tag) != 1) goto cleanup;

    success = true;

cleanup:
    EVP_CIPHER_CTX_free(ctx);
    return success;
}

// Допоміжна функція AES-256-GCM розшифрування
static bool aes_gcm_decrypt(const uint8_t *key, const uint8_t *iv,
                            const uint8_t *aad, size_t aad_len,
                            const uint8_t *cipher, size_t cipher_len,
                            const uint8_t *tag, uint8_t *plain) {
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx) return false;

    int len = 0;
    bool success = false;

    if (EVP_DecryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL) != 1) goto cleanup;
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, GCM_IV_SIZE, NULL) != 1) goto cleanup;
    if (EVP_DecryptInit_ex(ctx, NULL, NULL, key, iv) != 1) goto cleanup;

    // Передача AAD
    if (aad && aad_len > 0) {
        if (EVP_DecryptUpdate(ctx, NULL, &len, aad, (int)aad_len) != 1) goto cleanup;
    }

    // Розшифрування
    if (EVP_DecryptUpdate(ctx, plain, &len, cipher, (int)cipher_len) != 1) goto cleanup;

    // Встановлення очікуваного тегу перед фіналізацією
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_TAG, GCM_TAG_SIZE, (void*)tag) != 1) goto cleanup;

    // Перевірка цілісності: якщо тег не зійшовся, EVP_DecryptFinal_ex повертає <= 0
    if (EVP_DecryptFinal_ex(ctx, plain + len, &len) != 1) goto cleanup;

    success = true;

cleanup:
    EVP_CIPHER_CTX_free(ctx);
    return success;
}

// Запечатування даних у конверт
bool envelope_seal(const uint8_t *kek, const uint8_t *aad, size_t aad_len,
                   const uint8_t *data, size_t data_len, envelope_t *env) {
    uint8_t raw_dek[KEY_SIZE_256];
    bool status = false;

    // 1. Генерація криптографічно стійкого випадкового DEK та IV
    if (RAND_bytes(raw_dek, KEY_SIZE_256) != 1) return false;
    if (RAND_bytes(env->iv_dek, GCM_IV_SIZE) != 1) goto scrub_dek;
    if (RAND_bytes(env->iv_data, GCM_IV_SIZE) != 1) goto scrub_dek;

    env->ciphertext = (uint8_t*)malloc(data_len);
    if (!env->ciphertext) goto scrub_dek;
    env->ciphertext_len = data_len;

    // 2. Шифрування корисних даних згенерованим DEK
    if (!aes_gcm_encrypt(raw_dek, env->iv_data, aad, aad_len,
                         data, data_len, env->ciphertext, env->tag_data)) {
        free(env->ciphertext);
        env->ciphertext = NULL;
        goto scrub_dek;
    }

    // 3. Обгортання DEK довгостроковим ключем KEK
    uint8_t dek_tag[GCM_TAG_SIZE];
    if (!aes_gcm_encrypt(kek, env->iv_dek, aad, aad_len,
                         raw_dek, KEY_SIZE_256, env->wrapped_dek, dek_tag)) {
        free(env->ciphertext);
        env->ciphertext = NULL;
        goto scrub_dek;
    }
    memcpy(env->wrapped_dek + KEY_SIZE_256, dek_tag, GCM_TAG_SIZE);

    status = true;

scrub_dek:
    // 4. Обов'язкове занулення відкритого ключа DEK у пам'яті
    OPENSSL_cleanse(raw_dek, KEY_SIZE_256);
    return status;
}

// Розпечатування конверта
bool envelope_open(const uint8_t *kek, const uint8_t *aad, size_t aad_len,
                   const envelope_t *env, uint8_t *out_data) {
    uint8_t raw_dek[KEY_SIZE_256];
    bool status = false;

    // 1. Розгортання DEK за допомогою KEK
    const uint8_t *dek_tag = env->wrapped_dek + KEY_SIZE_256;
    if (!aes_gcm_decrypt(kek, env->iv_dek, aad, aad_len,
                         env->wrapped_dek, KEY_SIZE_256, dek_tag, raw_dek)) {
        return false; // Помилка автентифікації KEK або AAD
    }

    // 2. Розшифрування корисного навантаження отриманим DEK
    if (!aes_gcm_decrypt(raw_dek, env->iv_data, aad, aad_len,
                         env->ciphertext, env->ciphertext_len, env->tag_data, out_data)) {
        goto scrub_dek; // Помилка цілісності тіла даних
    }

    status = true;

scrub_dek:
    // 3. Негайне занулення DEK після використання
    OPENSSL_cleanse(raw_dek, KEY_SIZE_256);
    return status;
}
