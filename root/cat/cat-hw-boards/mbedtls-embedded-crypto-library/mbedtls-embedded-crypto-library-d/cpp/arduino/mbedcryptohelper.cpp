#include <Arduino.h>
#include "mbedtls/sha256.h"
#include "mbedtls/aes.h"

class MbedCryptoHelper {
public:
    static bool computeSHA256(const uint8_t *data, size_t len, uint8_t hashOut[32]) {
        mbedtls_sha256_context ctx;
        mbedtls_sha256_init(&ctx);
        
        if (mbedtls_sha256_starts_ret(&ctx, 0) != 0) {
            mbedtls_sha256_free(&ctx);
            return false;
        }
        if (mbedtls_sha256_update_ret(&ctx, data, len) != 0) {
            mbedtls_sha256_free(&ctx);
            return false;
        }
        if (mbedtls_sha256_finish_ret(&ctx, hashOut) != 0) {
            mbedtls_sha256_free(&ctx);
            return false;
        }
        
        mbedtls_sha256_free(&ctx);
        return true;
    }

    static bool encryptAES256(const uint8_t key[32], uint8_t iv[16],
                              const uint8_t *inData, size_t inLen, uint8_t *outData) {
        mbedtls_aes_context aes;
        mbedtls_aes_init(&aes);
        
        if (mbedtls_aes_setkey_enc(&aes, key, 256) != 0) {
            mbedtls_aes_free(&aes);
            return false;
        }
        
        int res = mbedtls_aes_crypt_cbc(&aes, MBEDTLS_AES_ENCRYPT, inLen, iv, inData, outData);
        mbedtls_aes_free(&aes);
        return (res == 0);
    }
};
