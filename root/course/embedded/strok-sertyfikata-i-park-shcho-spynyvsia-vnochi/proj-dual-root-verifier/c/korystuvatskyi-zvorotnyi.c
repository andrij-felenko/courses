int custom_tls_verify_callback(void *data, mbedtls_x509_crt *crt, int depth, uint32_t *flags) {
    /* Отримуємо бітову маску помилок валідації Mbed TLS */
    uint32_t validation_flags = *flags;

    /* Якщо єдина проблема полягає у невідповідності часу (сертифікат ще не діє або прострочений) */
    if (validation_flags == MBEDTLS_X509_BADCERT_EXPIRED || 
        validation_flags == MBEDTLS_X509_BADCERT_FUTURE) {
        
        bool is_emergency_bootstrap_mode = (bool)(uintptr_t)data;
        if (is_emergency_bootstrap_mode) {
            /* В аварійному режимі відновлення тимчасово ігноруємо помилку часу для виділеного сервера */
            *flags &= ~(MBEDTLS_X509_BADCERT_EXPIRED | MBEDTLS_X509_BADCERT_FUTURE);
            return 0;
        }
    }

    /* Якщо пошкоджено цифровий підпис або ім'я вузла не збігається — жорстке блокування */
    if (validation_flags & (MBEDTLS_X509_BADCERT_NOT_TRUSTED | MBEDTLS_X509_BADCERT_BAD_KEY)) {
        return -1;
    }

    return 0;
}
