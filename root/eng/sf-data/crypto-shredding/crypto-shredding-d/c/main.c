#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/crypto.h>

#define AES_256_KEY_SIZE 32
#define GCM_IV_SIZE      12
#define GCM_TAG_SIZE     16

typedef struct {
    uint8_t iv[GCM_IV_SIZE];
    uint8_t tag[GCM_TAG_SIZE];
    uint8_t *ciphertext;
    size_t ciphertext_len;
} EncryptedField;

typedef struct {
    uint8_t key[AES_256_KEY_SIZE];
    bool is_valid;
} SubjectKey;

/* Генерація криптографічно стійкого ключа DEK */
bool generate_subject_key(SubjectKey *out_key) {
    if (!out_key) return false;
    if (RAND_bytes(out_key->key, AES_256_KEY_SIZE) != 1) {
        return false;
    }
    out_key->is_valid = true;
    return true;
}

/* Безпечне знищення ключа в пам'яті (Crypto-shredding) */
void shred_subject_key(SubjectKey *target_key) {
    if (!target_key) return;
    OPENSSL_cleanse(target_key->key, AES_256_KEY_SIZE);
    target_key->is_valid = false;
}

/* Шифрування відкритого тексту за допомогою AES-256-GCM */
bool encrypt_pii_field(const SubjectKey *key,
                       const uint8_t *plaintext, size_t plaintext_len,
                       EncryptedField *out_field) {
    if (!key || !key->is_valid || !plaintext || !out_field) {
        return false;
    }

    /* Генерація унікального вектора ініціалізації (Nonce) */
    if (RAND_bytes(out_field->iv, GCM_IV_SIZE) != 1) {
        return false;
    }

    out_field->ciphertext = (uint8_t *)malloc(plaintext_len);
    if (!out_field->ciphertext) return false;

    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx) {
        free(out_field->ciphertext);
        out_field->ciphertext = NULL;
        return false;
    }

    int len = 0;
    bool success = false;

    if (EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL) == 1 &&
        EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, GCM_IV_SIZE, NULL) == 1 &&
        EVP_EncryptInit_ex(ctx, NULL, NULL, key->key, out_field->iv) == 1 &&
        EVP_EncryptUpdate(ctx, out_field->ciphertext, &len, plaintext, (int)plaintext_len) == 1) {
        
        out_field->ciphertext_len = (size_t)len;
        
        if (EVP_EncryptFinal_ex(ctx, out_field->ciphertext + len, &len) == 1 &&
            EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_GET_TAG, GCM_TAG_SIZE, out_field->tag) == 1) {
            out_field->ciphertext_len += (size_t)len;
            success = true;
        }
    }

    EVP_CIPHER_CTX_free(ctx);
    if (!success) {
        free(out_field->ciphertext);
        out_field->ciphertext = NULL;
    }
    return success;
}

/* Розшифрування шифротексту з обов'язковою верифікацією тегу GMAC */
bool decrypt_pii_field(const SubjectKey *key,
                       const EncryptedField *in_field,
                       uint8_t *out_plaintext, size_t *out_plaintext_len) {
    if (!key || !key->is_valid || !in_field || !out_plaintext || !out_plaintext_len) {
        return false;
    }

    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx) return false;

    int len = 0;
    bool success = false;

    if (EVP_DecryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL) == 1 &&
        EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, GCM_IV_SIZE, NULL) == 1 &&
        EVP_DecryptInit_ex(ctx, NULL, NULL, key->key, in_field->iv) == 1 &&
        EVP_DecryptUpdate(ctx, out_plaintext, &len, in_field->ciphertext, (int)in_field->ciphertext_len) == 1) {
        
        *out_plaintext_len = (size_t)len;
        
        /* Встановлення очікуваного тегу автентифікації перед завершенням */
        if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_TAG, GCM_TAG_SIZE, (void *)in_field->tag) == 1) {
            if (EVP_DecryptFinal_ex(ctx, out_plaintext + len, &len) == 1) {
                *out_plaintext_len += (size_t)len;
                out_plaintext[*out_plaintext_len] = '\0';
                success = true;
            }
        }
    }

    EVP_CIPHER_CTX_free(ctx);
    if (!success) {
        /* При помилці автентифікації буфер очищається від часткових байтів */
        OPENSSL_cleanse(out_plaintext, in_field->ciphertext_len);
        *out_plaintext_len = 0;
    }
    return success;
}
