#include "mbedtls/x509_crt.h"
#include "mbedtls/ctr_drbg.h"
#include "mbedtls/entropy.h"

// Коректний порядок звільнення криптографічних контекстів mbedTLS
void cleanup_crypto_resources(mbedtls_x509_crt *crt_chain,
                              mbedtls_ctr_drbg_context *ctr_drbg,
                              mbedtls_entropy_context *entropy) {
    // 1. Звільняємо ланцюжок сертифікатів X.509
    if (crt_chain != NULL) {
        mbedtls_x509_crt_free(crt_chain);
    }

    // 2. Звільняємо генератор псевдовипадкових чисел CTR-DRBG
    if (ctr_drbg != NULL) {
        mbedtls_ctr_drbg_free(ctr_drbg);
    }

    // 3. Звільняємо колектор ентропії
    if (entropy != NULL) {
        mbedtls_entropy_free(entropy);
    }
}
