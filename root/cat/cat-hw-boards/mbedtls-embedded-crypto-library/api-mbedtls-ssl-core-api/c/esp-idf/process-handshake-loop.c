#include "mbedtls/ssl.h"

// Циклічний автомат обслуговування неблокуючого рукостискання mbedTLS
int process_handshake_loop(mbedtls_ssl_context *ssl) {
    int ret;
    do {
        ret = mbedtls_ssl_handshake(ssl);
        if (ret == MBEDTLS_ERR_SSL_WANT_READ || ret == MBEDTLS_ERR_SSL_WANT_WRITE) {
            // Повертаємо контроль головному циклу для очікування подій I/O
            return ret;
        }
    } while (ret == 0 && ssl->state != MBEDTLS_SSL_HANDSHAKE_OVER);

    return ret; // 0 — успіх, від'ємне значення — фатальна помилка
}

// Безпечне читання прикладних даних з обробкою закриття сесії
int safe_read_data(mbedtls_ssl_context *ssl, unsigned char *buf, size_t len) {
    int ret = mbedtls_ssl_read(ssl, buf, len);

    if (ret == MBEDTLS_ERR_SSL_WANT_READ) {
        return 0; // Даних немає, чекаємо наступної ітерації
    }
    if (ret == MBEDTLS_ERR_SSL_PEER_CLOSE_NOTIFY) {
        // Віддалений вузол коректно закрив TLS-сесію
        mbedtls_ssl_close_notify(ssl);
        return -1;
    }
    if (ret < 0) {
        // Фатальна помилка дешифрування або мережі
        return ret;
    }

    return ret; // Кількість байтів прикладного корисного навантаження
}
