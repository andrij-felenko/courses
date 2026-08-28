int tls_client_config(void) {
    // 1. типові значення: МИ — КЛІЄНТ, транспорт — потік (TCP), пресет default.
    //    саме тут mbedTLS проставляє розумні дефолти під наш профіль.
    if (mbedtls_ssl_config_defaults(&conf,
            MBEDTLS_SSL_IS_CLIENT,
            MBEDTLS_SSL_TRANSPORT_STREAM,     // потік = поверх TCP (не DTLS)
            MBEDTLS_SSL_PRESET_DEFAULT) != 0)
        return -1;

    // 2. джерело випадковості — у конфіг.
    mbedtls_ssl_conf_rng(&conf, mbedtls_ctr_drbg_random, &ctr_drbg);

    // 3. ★ ОБОВ'ЯЗКОВА перевірка сертифіката сервера. Це — головний рядок.
    //    VERIFY_REQUIRED: сервер МУСИТЬ показати сертифікат, ланцюг МУСИТЬ
    //    зійтися до нашого кореня, інакше рукостискання провалиться.
    mbedtls_ssl_conf_authmode(&conf, MBEDTLS_SSL_VERIFY_REQUIRED);

    // 4. ★ той самий корінь довіри — у ланцюг. Без цього рядка VERIFY_REQUIRED
    //    не має ЧИМ перевіряти: mbedTLS вимагатиме CA-ланцюг і рукостискання
    //    впаде з помилкою «CA chain required» (див. пастку нижче).
    mbedtls_ssl_conf_ca_chain(&conf, &cacert, NULL);

    // 5. (Flash+CPU) запропонувати серверу РІВНО ті криві, що ми скомпілювали.
    //    список ОБИРАЄ лише зі скомпільованого; порядок = наш пріоритет.
    static const uint16_t groups[] = {
        MBEDTLS_SSL_IANA_TLS_GROUP_X25519,    // єдина крива, яку ми лишили
        0,                                    // 0 — кінець списку
    };
    mbedtls_ssl_conf_groups(&conf, groups);

    return 0;
}
