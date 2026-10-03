#include "mbedtls/ssl.h"
#include "mbedtls/ctr_drbg.h"
#include "mbedtls/entropy.h"

// Ініціалізація статичної конфігурації та динамічного контексту mbedTLS
int init_tls_core(mbedtls_ssl_config *conf, mbedtls_ssl_context *ssl,
                  mbedtls_ctr_drbg_context *ctr_drbg) {
    int ret;

    // Ініціалізація структур порожніми значеннями
    mbedtls_ssl_config_init(conf);
    mbedtls_ssl_init(ssl);

    // Завантаження базових налаштувань для TLS-клієнта по протоколу TCP
    ret = mbedtls_ssl_config_defaults(conf,
                                      MBEDTLS_SSL_IS_CLIENT,
                                      MBEDTLS_SSL_TRANSPORT_STREAM,
                                      MBEDTLS_SSL_PRESET_DEFAULT);
    if (ret != 0) {
        return ret;
    }

    // Реєстрація генератора випадкових чисел (RNG)
    mbedtls_ssl_conf_rng(conf, mbedtls_ctr_drbg_random, ctr_drbg);

    // Прив'язка конфігурації до контексту сесії та виділення буферів
    ret = mbedtls_ssl_setup(ssl, conf);
    if (ret != 0) {
        mbedtls_ssl_free(ssl);
        mbedtls_ssl_config_free(conf);
        return ret;
    }

    return 0;
}
