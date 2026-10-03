#include <stdio.h>
#include <string.h>
#include "mbedtls/entropy.h"
#include "mbedtls/ctr_drbg.h"

// Ініціалізація колектора ентропії та генератора CTR-DRBG
int crypto_init_entropy_and_drbg(mbedtls_entropy_context *entropy,
                                  mbedtls_ctr_drbg_context *ctr_drbg) {
    const unsigned char pers[] = "mbedtls_esp32_drbg";
    int ret;

    mbedtls_entropy_init(entropy);
    mbedtls_ctr_drbg_init(ctr_drbg);

    // Зв'язування генератора CTR-DRBG із колектором ентропії
    ret = mbedtls_ctr_drbg_seed(ctr_drbg, mbedtls_entropy_func, entropy,
                                pers, strlen((const char *)pers));
    if (ret != 0) {
        mbedtls_ctr_drbg_free(ctr_drbg);
        mbedtls_entropy_free(entropy);
        return ret;
    }

    return 0;
}

// Генерація випадкового масиву заданої довжини
int crypto_get_random_bytes(mbedtls_ctr_drbg_context *ctr_drbg,
                            unsigned char *output, size_t len) {
    return mbedtls_ctr_drbg_random(ctr_drbg, output, len);
}
