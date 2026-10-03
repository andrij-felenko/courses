#include "mbedtls/entropy.h"
#include "mbedtls/ctr_drbg.h"

#define SOC_RNG_DATA_REG (*(volatile uint32_t *)(0x3FF20E44))

/* Коллбек зчитування апаратної ентропії для mbedTLS */
int hardware_trng_entropy_poll(void *data, unsigned char *output,
                               size_t len, size_t *olen) {
    size_t written = 0;
    while (written < len) {
        uint32_t random_val = SOC_RNG_DATA_REG;
        size_t to_copy = (len - written > 4) ? 4 : (len - written);
        memcpy(output + written, &random_val, to_copy);
        written += to_copy;
    }
    *olen = written;
    return 0;
}

int init_crypto_random_system(mbedtls_entropy_context *entropy,
                               mbedtls_ctr_drbg_context *ctr_drbg) {
    mbedtls_entropy_init(entropy);
    mbedtls_ctr_drbg_init(ctr_drbg);

    /* Реєстрація апаратного TRNG як сильного джерела ентропії */
    int ret = mbedtls_entropy_add_source(entropy, hardware_trng_entropy_poll,
                                         NULL, 32, MBEDTLS_ENTROPY_SOURCE_STRONG);
    if (ret != 0) {
        return ret;
    }

    const char *pers = "tls_client_ctx";
    return mbedtls_ctr_drbg_seed(ctr_drbg, mbedtls_entropy_func, entropy,
                                 (const unsigned char *)pers, strlen(pers));
}
