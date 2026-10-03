#include <stdio.h>
#include <string.h>
#include "mbedtls/sha256.h"
#include "mbedtls/aes.h"

// Обчислення SHA-256 дайджесту від вхідного буфера
int crypto_compute_sha256(const unsigned char *input, size_t ilen, unsigned char output[32]) {
    mbedtls_sha256_context sha_ctx;
    
    mbedtls_sha256_init(&sha_ctx);
    int ret = mbedtls_sha256_starts_ret(&sha_ctx, 0); // 0 для SHA-256
    if (ret != 0) {
        mbedtls_sha256_free(&sha_ctx);
        return ret;
    }
    
    ret = mbedtls_sha256_update_ret(&sha_ctx, input, ilen);
    if (ret != 0) {
        mbedtls_sha256_free(&sha_ctx);
        return ret;
    }
    
    ret = mbedtls_sha256_finish_ret(&sha_ctx, output);
    mbedtls_sha256_free(&sha_ctx);
    return ret;
}

// Зашифрування блоку даних у режимі AES-256-CBC
int crypto_encrypt_aes_cbc(const unsigned char key[32], unsigned char iv[16],
                           const unsigned char *input, size_t ilen, unsigned char *output) {
    mbedtls_aes_context aes_ctx;
    
    mbedtls_aes_init(&aes_ctx);
    int ret = mbedtls_aes_setkey_enc(&aes_ctx, key, 256);
    if (ret != 0) {
        mbedtls_aes_free(&aes_ctx);
        return ret;
    }
    
    // Вхідна довжина повинна бути кратною 16 байтам (розмір блоку AES)
    ret = mbedtls_aes_crypt_cbc(&aes_ctx, MBEDTLS_AES_ENCRYPT, ilen, iv, input, output);
    mbedtls_aes_free(&aes_ctx);
    return ret;
}
