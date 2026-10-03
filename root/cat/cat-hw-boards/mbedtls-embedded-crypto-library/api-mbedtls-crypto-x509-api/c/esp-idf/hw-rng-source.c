#include "mbedtls/entropy.h"
#include "mbedtls/ctr_drbg.h"
#include <string.h>

// Кастомна функція зчитування апаратної ентропії SoC ESP8266
static int hw_rng_source(void *data, unsigned char *output, size_t len, size_t *olen) {
    uint32_t rng_val;
    size_t i;
    for (i = 0; i < len; i += 4) {
        rng_val = *((volatile uint32_t *)0x3FF20E44); // Апаратний регістр RNG ESP8266
        size_t to_copy = (len - i < 4) ? (len - i) : 4;
        memcpy(output + i, &rng_val, to_copy);
    }
    *olen = len;
    return 0;
}

// Ініціалізація та посів криптографічного генератора випадкових чисел
int init_crypto_rng(mbedtls_entropy_context *entropy, mbedtls_ctr_drbg_context *ctr_drbg) {
    int ret;
    const char *pers = "esp8266_mbedtls_client";

    mbedtls_entropy_init(entropy);
    mbedtls_ctr_drbg_init(ctr_drbg);

    // Додаємо апаратне джерело ентропії (сильне джерело, поріг 32 байти)
    ret = mbedtls_entropy_add_source(entropy, hw_rng_source, NULL, 32, MBEDTLS_ENTROPY_SOURCE_STRONG);
    if (ret != 0) {
        return ret;
    }

    // Посів генератора CTR-DRBG від контексту ентропії
    ret = mbedtls_ctr_drbg_seed(ctr_drbg, mbedtls_entropy_func, entropy,
                                (const unsigned char *)pers, strlen(pers));
    if (ret != 0) {
        mbedtls_ctr_drbg_free(ctr_drbg);
        mbedtls_entropy_free(entropy);
        return ret;
    }

    return 0;
}
