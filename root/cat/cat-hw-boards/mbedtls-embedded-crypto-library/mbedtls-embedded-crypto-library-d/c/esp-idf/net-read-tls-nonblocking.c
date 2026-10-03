#include <stdio.h>
#include <string.h>
#include "mbedtls/ssl.h"
#include "mbedtls/error.h"

// Зчитування даних із неблокуючого TLS-контексту
int net_read_tls_nonblocking(mbedtls_ssl_context *ssl, unsigned char *buf,
                             size_t len, size_t *out_len) {
    int ret = mbedtls_ssl_read(ssl, buf, len);

    if (ret > 0) {
        *out_len = (size_t)ret;
        return 0; // Дані успішно прочитані
    }

    if (ret == MBEDTLS_ERR_SSL_WANT_READ || ret == MBEDTLS_ERR_SSL_WANT_WRITE) {
        // Мережевий буфер порожній, повертаємо код затримки для повторної спроби
        return ret;
    }

    // Форматування від'ємного коду помилки у текстовий рядок діагностики
    char err_buf[128];
    mbedtls_strerror(ret, err_buf, sizeof(err_buf));
    printf("Помилка TLS mbedTLS: -0x%04X (%s)\n", -ret, err_buf);

    return ret;
}
