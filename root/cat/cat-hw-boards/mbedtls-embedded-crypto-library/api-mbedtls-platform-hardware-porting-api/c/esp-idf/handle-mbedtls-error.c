#include "mbedtls/ssl.h"
#include "mbedtls/error.h"

void handle_mbedtls_error(int error_code, mbedtls_ssl_context *ssl,
                           mbedtls_ssl_config *conf) {
    char error_buf[100];
    mbedtls_strerror(error_code, error_buf, sizeof(error_buf));
    // Логування помилки mbedTLS

    /* Звільнення контекстів mbedTLS */
    if (ssl != NULL) {
        mbedtls_ssl_free(ssl);
    }
    if (conf != NULL) {
        mbedtls_ssl_config_free(conf);
    }

    /* Відновлення апаратного криптомодуля при помилках периферії */
    if (error_code == MBEDTLS_ERR_AES_HW_ACCEL_FAILED) {
        /* Скидання периферійного блоку AES через регістр скидання SoC */
        volatile uint32_t *rst_reg = (volatile uint32_t *)0x60000020;
        *rst_reg |= (1 << 5);  /* Установка біта скидання */
        *rst_reg &= ~(1 << 5); /* Зняття біта скидання */
    }
}

int execute_secure_tls_handshake(mbedtls_ssl_context *ssl) {
    int ret = mbedtls_ssl_handshake(ssl);
    if (ret != 0) {
        handle_mbedtls_error(ret, ssl, NULL);
        return ret;
    }
    return 0;
}
